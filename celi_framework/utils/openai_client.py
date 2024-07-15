"""Supports OpenAI or any other LLMs that implement the OpenAI aAPI"""

import functools
import os
from typing import Optional

import openai
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall

from celi_framework.utils.llm_response import LLMResponse, ToolCall


@functools.lru_cache()
def get_openai_client(base_url: Optional[str] = None):
    return openai.AsyncOpenAI(
        base_url=base_url, api_key=os.environ.get("OPENAI_API_KEY", None)
    )


async def openai_chat_completion(base_url: str, **kwargs):
    resp = await get_openai_client(
        base_url=base_url,
    ).chat.completions.create(**kwargs)
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
