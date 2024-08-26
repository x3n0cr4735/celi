import functools
import json
import logging
import os

from anthropic import AsyncAnthropic, AsyncAnthropicBedrock
from anthropic.types import ToolUseBlock, Message

from celi_framework.utils.llm_response import LLMResponse, ToolCall, FunctionCall

logger = logging.getLogger(__name__)


@functools.lru_cache()
def get_anthropic_bedrock_client():
    try:
        if aws_region is None:
            aws_region = os.environ.get("AWS_REGION") or "us-west-2"
            logging.info("AWS region not defined. Defaulting to 'us-west-2'.")
    except NameError:
        aws_region = os.environ.get("AWS_REGION") or "us-west-2"
        logging.info("AWS region not defined. Defaulting to 'us-west-2'.")
    return AsyncAnthropicBedrock(aws_region=aws_region)


@functools.lru_cache()
def get_anthropic_client():
    return AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


async def anthropic_bedrock_chat_completion(**kwargs):
    cleaned_kwargs = _convert_openai_to_anthropic_input(**kwargs)
    resp = await get_anthropic_bedrock_client().messages.create(**cleaned_kwargs)
    return _parse_anthropic_response(resp)


async def anthropic_chat_completion(**kwargs):
    cleaned_kwargs = _convert_openai_to_anthropic_input(**kwargs)
    resp = await get_anthropic_client().messages.create(**cleaned_kwargs)
    return _parse_anthropic_response(resp)


def _convert_openai_to_anthropic_input(**kwargs):
    """Adjust OpenAI options to support Anthropic API."""

    # remove arguments not supported by Anthropic
    remaining_kwargs = {
        k: v
        for k, v in kwargs.items()
        if k not in ["response_format", "seed", "tools", "tool_choice"] and (k != "temperature" or v is not None)
    }

    def fix_tool(t):
        assert t["type"] == "function", "OpenAI API only allows 'function' tools"
        tool = t["function"]
        tool = {
            ("input_schema" if k == "parameters" else k): v for k, v in tool.items()
        }
        return tool

    # Tools have a different format
    tools = (
        {"tools": [fix_tool(_) for _ in kwargs["tools"]]}
        if "tools" in kwargs and kwargs["tools"] is not None
        else {}
    )

    # Tool choice has a different format, and can only be specified if tools are present
    tool_choice = (
        {"tool_choice": {"type": kwargs["tool_choice"]}}
        if "tool_choice" in kwargs and "tools" in tools and len(tools["tools"]) > 0
        else {}
    )

    # System message is a separate argument.
    extract_system_messages = [
        m["content"] for m in kwargs["messages"] if m["role"] == "system"
    ]
    assert len(extract_system_messages) <= 1, "Only one system message is allowed"
    system_message = (
        {"system": extract_system_messages[0]} if extract_system_messages else {}
    )

    # Can't have repeated 'user' messages:
    # Current "function" to a "user" message
    current_role = None
    deduped_messages = []
    non_system_messages = [m for m in kwargs["messages"] if m["role"] != "system"]
    for m in non_system_messages:
        clean_m = (
            {"role": "user", "content": m["content"]} if m["role"] == "function" else m
        )
        if clean_m["role"] != current_role:
            deduped_messages.append(clean_m)
        else:
            deduped_messages[-1] = {
                **deduped_messages[-1],
                "content": deduped_messages[-1]["content"]
                + "\n\n"
                + clean_m["content"],
            }
        current_role = clean_m["role"]

    # Can't end with an 'assistant' message when using tool calls.
    if deduped_messages[-1]["role"] == "assistant":
        deduped_messages.append(
            {"role": "user", "content": "Please continue executing the tasks."}
        )

    # Max tokens has to be specified
    max_tokens = (
        {"max_tokens": 4096}
        if "max_tokens" not in remaining_kwargs
        or remaining_kwargs["max_tokens"] is None
        else {}
    )

    cleaned_kwargs = {
        **remaining_kwargs,
        "messages": deduped_messages,
        **system_message,
        **tool_choice,
        **tools,
        **max_tokens,
    }
    return cleaned_kwargs


def _map_stop_reason(stop_reason):
    match stop_reason:
        case "max_tokens":
            return "length"
        case "end_turn":
            return "stop"
        case "tool_use":
            return "tool_calls"
        case _:
            assert False, f"Unexpected stop reason {stop_reason}"


def _parse_anthropic_response(resp: Message):
    text = "\n".join(_.text for _ in resp.content if _.type == "text")

    def convert_tool(t: ToolUseBlock):
        args = json.dumps(t.input)
        return ToolCall(
            id=t.id,
            type="function",
            function=FunctionCall(
                arguments=args,
                name=t.name,
            ),
        )

    tools = [convert_tool(_) for _ in resp.content if _.type == "tool_use"]
    return LLMResponse(
        content=text,
        finish_reason=_map_stop_reason(resp.stop_reason),
        tool_calls=tools if tools else None,
    )
