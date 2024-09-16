import functools
import json
import logging
import os
from json import JSONDecodeError

import boto3
from anthropic import AsyncAnthropic, AsyncAnthropicBedrock
from anthropic.types import ToolUseBlock, Message

from celi_framework.utils.llm_response import LLMResponse, ToolCall, FunctionCall

logger = logging.getLogger(__name__)


@functools.lru_cache()
def get_anthropic_bedrock_client():

    args={}
    #Default the AWS region to us-west-2
    aws_region = os.environ.get("AWS_REGION", None)
    if aws_region is None:
        aws_region = "us-west-2"
        logging.info("AWS region not defined. Defaulting to 'us-west-2'.")
    args = {"aws_region": aws_region}
        
    if "AWS_PROFILE" in os.environ:
        session = boto3.Session(profile_name=os.environ["AWS_PROFILE"])
        credentials = session.get_credentials()
        args.update({
            "aws_access_key": credentials.access_key,
            "aws_secret_key": credentials.secret_key,
        })
    return AsyncAnthropicBedrock(**args)


@functools.lru_cache()
def get_anthropic_client():
    return AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


async def anthropic_bedrock_chat_completion(**kwargs):
    cleaned_kwargs = _convert_openai_to_anthropic_input(**kwargs)
    # logger.debug(f"Anthropic input:\n{cleaned_kwargs}")
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
        if k not in ["response_format", "seed", "tools", "tool_choice"]
        and (k != "temperature" or v is not None)
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
        {
            "tool_choice": {
                "type": (
                    "any"
                    if kwargs["tool_choice"] == "required"
                    else kwargs["tool_choice"]
                )
            }
        }
        if "tool_choice" in kwargs and "tools" in tools and len(tools["tools"]) > 0
        else {}
    )

    extract_system_messages = []
    reformatted_messages = []
    for m in kwargs["messages"]:
        match m["role"]:
            case "system":
                # System message is a separate argument.
                extract_system_messages.append(m["content"])
            case "user":
                if m["content"]:
                    reformatted_messages.append(m)
            case "assistant":
                if m["content"]:
                    reformatted_messages.append(m)
            case "function":
                # Function calls get split into 2 messages, a call and a response.
                try:
                    arg_dict = json.loads(m["arguments"])
                except JSONDecodeError:
                    arg_dict = {"invalid_arguments": m["arguments"]}
                func_call = {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": m["id"],
                            "name": m["name"],
                            "input": arg_dict,
                        }
                    ],
                }
                func_response = {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": m["id"],
                            "content": m["return_value"],
                            "is_error": m["is_error"],
                        }
                    ],
                }
                reformatted_messages.append(func_call)
                reformatted_messages.append(func_response)
            case x:
                raise ValueError(f"Unknown role {x}")

    assert len(extract_system_messages) <= 1, "Only one system message is allowed"
    system_message = (
        {"system": extract_system_messages[0]} if extract_system_messages else {}
    )

    # Combine adjacent messages with the same role
    current_role = None
    deduped_messages = []
    for m in reformatted_messages:
        if m["role"] != current_role:
            deduped_messages.append({**m})
            current_role = m["role"]
        else:
            original_content = deduped_messages[-1]["content"]
            if isinstance(original_content, str):
                original_content = [{"type": "text", "text": original_content}]
            new_content = m["content"]
            if isinstance(new_content, str):
                new_content = [{"type": "text", "text": new_content}]
            deduped_messages[-1]["content"] = original_content + new_content

    # Can't end with an 'assistant' message when using tool calls.
    if deduped_messages[-1]["role"] == "assistant":
        deduped_messages.append(
            {
                "role": "user",
                "content": "Think step by step and then make the tool call you need to accomplish the task.",
            }
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
    # logger.debug(f"Raw anthropic response: {resp}")
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
