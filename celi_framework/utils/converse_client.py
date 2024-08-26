import functools
import json
import logging
import os
import boto3
import aioboto3

from celi_framework.utils.llm_response import LLMResponse, ToolCall, FunctionCall

logger = logging.getLogger(__name__)


@functools.lru_cache()
def get_converse_bedrock_client(model_name):
    try:
        if aws_region is None:
            aws_region = os.environ.get("AWS_REGION") or "us-west-2"
            logging.info("AWS region not defined. Defaulting to 'us-west-2'.")
    except NameError:
        aws_region = os.environ.get("AWS_REGION") or "us-west-2"
        logging.info("AWS region not defined. Defaulting to 'us-west-2'.")
    
    session = aioboto3.Session(region_name = aws_region)
    return session

async def converse_bedrock_chat_completion(**kwargs):
    cleaned_kwargs = _convert_openai_to_converse_input(**kwargs)
    async with get_converse_bedrock_client(kwargs.get('model')).client('bedrock-runtime') as client:
        resp = await client.converse(**cleaned_kwargs)
    return _parse_converse_response(resp)

def _convert_openai_to_converse_input(**kwargs):
    """Adjust OpenAI options to support Converse API."""

    # Check if "tools" are present in kwargs and raise an error if they are
    if "tools" in kwargs and kwargs["tools"] is not None:
        raise ValueError("The 'tools' parameter is not yet supported by the CELI implementation of AWS Bedrock models. Try using a different model e.g. through OpenAI or Anthropic.")

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

    # System message is a separate argument.
    extract_system_messages = [m["content"] for m in kwargs["messages"] if m["role"] == "system"]
    assert len(extract_system_messages) <= 1, "Only one system message is allowed"
    if extract_system_messages:
        system_message = [{"text": extract_system_messages[0]}]
    else:
        system_message = []  # or provide a default message if needed


    # Can't have repeated 'user' messages:
    # Current "function" to a "user" message
    current_role = None
    deduped_messages = []
    non_system_messages = [m for m in kwargs["messages"] if m["role"] != "system"]
    for m in non_system_messages:
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
    if deduped_messages[-1]["role"] == "assistant":
        deduped_messages.append({"role": "user", "content": [{"text": "Please continue executing the tasks."}]})

    cleaned_kwargs = {
        "modelId": kwargs.get("model"),
        "inferenceConfig": inference_config,
        "messages": deduped_messages,
        "system": system_message,
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


def _parse_converse_response(resp):
    text = "\n".join(item['text'] for item in resp['output']['message']['content'])

    return LLMResponse(
        content=text,
        finish_reason=_map_stop_reason(resp['stopReason']),
        #tool_calls=tools if tools else None,
        tool_calls=None
    )
