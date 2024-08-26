"""Supports OpenAI or any other LLMs that implement the OpenAI aAPI"""

import functools
import logging
import os
from typing import Optional

import openai
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall

from celi_framework.utils.llm_response import LLMResponse, ToolCall

logger = logging.getLogger(__name__)


@functools.lru_cache()
def get_openai_client(base_url: Optional[str] = None):
    logger.info("Creating OpenAI client")
    return openai.AsyncOpenAI(
        base_url=base_url, api_key=os.environ.get("OPENAI_API_KEY", None)
    )


async def openai_chat_completion(base_url: str, **kwargs):
    def clean_msg(m):
        return (
            {
                "role": "function",
                "name": m["name"],
                "content": f"Call to function {m['name']} with arguments {m['arguments']} returned\n{m['return_value']}",
            }
            if m["role"] == "function"
            else m
        )

    cleaned_messages = [clean_msg(m) for m in kwargs["messages"]]
    cleaned_args = {**kwargs, "messages": cleaned_messages}
    resp = await get_openai_client(
        base_url=base_url,
    ).chat.completions.create(**cleaned_args)
    # logger.debug(f"Received LLM response {resp}")
    return llm_response_from_chat_completion(resp)


def llm_response_from_chat_completion(resp: ChatCompletion):
    def convert_tool_call(tc: ChatCompletionMessageToolCall):
        return ToolCall.model_validate(tc.dict())

    tool_calls = (
        [convert_tool_call(_) for _ in resp.choices[0].message.tool_calls]
        if resp.choices[0].message.tool_calls
        else None
    )
    return LLMResponse(
        content=resp.choices[0].message.content,
        finish_reason=resp.choices[0].finish_reason,
        tool_calls=tool_calls,
    )
