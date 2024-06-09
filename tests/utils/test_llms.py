import logging
import os

import openai
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_ask_split():
    base_url = os.getenv("MODEL_API_URL", None)
    client = openai.OpenAI(
        base_url=base_url, api_key=os.environ.get("OPENAI_API_KEY", None)
    )
    ret = client.chat.completions.create(
        messages=[{"role": "user", "content": "the quick brown fox jumps over the"}],
        model=os.getenv("PRIMARY_LLM", None),
    )
    logger.info(f"LLM returned: {ret}")
