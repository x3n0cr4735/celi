"""Supports OpenAI or any other LLMs that implement the OpenAI aAPI"""

import functools
import os
from typing import Optional

import openai


@functools.lru_cache()
def get_openai_client(base_url: Optional[str] = None):
    return openai.AsyncOpenAI(
        base_url=base_url, api_key=os.environ.get("OPENAI_API_KEY", None)
    )


async def openai_chat_completion(base_url: str, **kwargs):
    return await get_openai_client(
        base_url=base_url,
    ).chat.completions.create(**kwargs)
