import functools
import os

import anthropic


@functools.lru_cache()
def get_anthropic_client():
    return anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


async def anthropic_chat_completion(**kwargs):
    return await get_anthropic_client().messages.create(**kwargs)
