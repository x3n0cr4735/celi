import logging

import pytest

from celi_framework.utils.anthropic_client import anthropic_chat_completion

logger = logging.getLogger(__name__)


@pytest.mark.skip
@pytest.mark.asyncio
async def test_ask_split():
    ret = await anthropic_chat_completion(
        messages=[{"role": "user", "content": "the quick brown fox jumps over the"}],
        model="claude-2.1",
        max_tokens=10,
    )
    logger.info(f"LLM returned: {ret}")
