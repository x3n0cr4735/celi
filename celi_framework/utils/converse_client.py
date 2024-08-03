import functools
import json
import logging
import os
import boto3

#from anthropic import AsyncAnthropic, AsyncAnthropicBedrock
#from anthropic.types import ToolUseBlock, Message

from celi_framework.utils.llm_response import LLMResponse, ToolCall, FunctionCall

logger = logging.getLogger(__name__)


@functools.lru_cache()
def get_converse_bedrock_client():
    return boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

async def converse_bedrock_chat_completion(**kwargs):
    #logger.info(kwargs.get("model"))
    cleaned_kwargs = _convert_openai_to_converse_input(**kwargs)
    resp = get_converse_bedrock_client().converse(**cleaned_kwargs)
    return _parse_converse_response(resp)

def _convert_openai_to_converse_input(**kwargs):
    """Adjust OpenAI options to support Converse API."""

    # remove arguments not supported by Converse
    remaining_kwargs = {
        k: v
        for k, v in kwargs.items()
        if k not in ["response_format", "seed", "tools", "tool_choice"] and (k != "temperature" or v is not None)
    }

    # Create inferenceConfig
    max_tokens = kwargs.get('max_tokens', None)
    stop_sequences = kwargs.get('stop_sequences', None)
    temperature = kwargs.get('temperature', None)
    top_p = kwargs.get('top_p', None)
    inference_config = {k: v for k, v in {
        "maxTokens": max_tokens,
        "stopSequences": stop_sequences,
        "temperature": temperature,
        "topP": top_p
    }.items() if v is not None}

    # def fix_tool(t):
    #     assert t["type"] == "function", "OpenAI API only allows 'function' tools"
    #     tool = t["function"]
    #     tool = {
    #         ("input_schema" if k == "parameters" else k): v for k, v in tool.items()
    #     }
    #     return tool

    # # Tools have a different format
    # tools = (
    #     {"tools": [fix_tool(_) for _ in kwargs["tools"]]}
    #     if "tools" in kwargs and kwargs["tools"] is not None
    #     else {}
    # )

    # # Tool choice has a different format, and can only be specified if tools are present
    # tool_choice = (
    #     {"tool_choice": {"type": kwargs["tool_choice"]}}
    #     if "tool_choice" in kwargs and "tools" in tools and len(tools["tools"]) > 0
    #     else {}
    # )
    
    # tool_config = {
    #     "toolChoice": tool_choice,
    #     "tools": tools
    # }

    # System message is a separate argument.
    extract_system_messages = [m["content"] for m in kwargs["messages"] if m["role"] == "system"]
    assert len(extract_system_messages) <= 1, "Only one system message is allowed"
    system_message = extract_system_messages if extract_system_messages else []

    # Can't have repeated 'user' messages:
    # Current "function" to a "user" message
    current_role = None
    deduped_messages = []
    non_system_messages = [m for m in kwargs["messages"] if m["role"] != "system"]
    for m in non_system_messages:
        # Ensure clean_m["content"] is a list of dicts
        if m["role"] == "function":
            clean_m = {"role": "user", "content": [{"text": m["content"]}]}
        else:
            clean_m = m
            clean_m["content"] = [{"text": clean_m["content"]}] if isinstance(clean_m["content"], str) else clean_m["content"]
        
        if clean_m["role"] != current_role:
            deduped_messages.append(clean_m)
        else:
            deduped_messages[-1]["content"] += clean_m["content"]
        current_role = clean_m["role"]
    #logger.info(f"clean_m: {clean_m}")
    if deduped_messages[-1]["role"] == "assistant":
        deduped_messages.append({"role": "user", "content": [{"text": "Please continue executing the tasks."}]})

    #logger.info(kwargs.get("model"))
    cleaned_kwargs = {
        "modelId": kwargs.get("model"),
        "inferenceConfig": inference_config,
        "messages": deduped_messages,
        "system": system_message,
        #"toolConfig": tool_config if tools else {"tools": [], "toolChoice": tool_choice}
    }
    #logger.info(cleaned_kwargs.get("modelId"))
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


def _parse_converse_response(resp):
    #logger.info(resp)
    text = "\n".join(item['text'] for item in resp['output']['message']['content'])

    # def convert_tool(t: ToolUseBlock):
    #     args = json.dumps(t.input)
    #     return ToolCall(
    #         id=t.id,
    #         type="function",
    #         function=FunctionCall(
    #             arguments=args,
    #             name=t.name,
    #         ),
    #     )

    # tools = [convert_tool(_) for _ in resp.content if _.type == "tool_use"]
    return LLMResponse(
        content=text,
        finish_reason=_map_stop_reason(resp['stopReason']),
        #tool_calls=tools if tools else None,
        tool_calls=None
    )
