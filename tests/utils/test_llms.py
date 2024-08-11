import logging
import os

import pytest

from celi_framework.utils.llm_cache import disable_llm_caching, enable_llm_caching
from celi_framework.utils.llms import quick_ask, ask_split, ToolDescription

logger = logging.getLogger(__name__)


@pytest.mark.skip
def test_quick_ask():
    ret = quick_ask(
        "Hello", model_name=os.getenv("PRIMARY_LLM", "gpt-4-turbo-2024-04-09")
    )
    assert type(ret) == str
    logger.info(f"LLM returned: {ret}")


@pytest.mark.skip
@pytest.mark.asyncio
async def test_ask_split_with_tools():
    try:
        await disable_llm_caching()
        ret = await ask_split(
            "Please call the test tool with value 1",
            system_message="You are a test for tool calls",
            model_name="gpt-4o-mini",
            tool_descriptions=[
                ToolDescription(
                    name="test",
                    description="Simple tool used in unit testing",
                    parameters={
                        "type": "object",
                        "properties": {
                            "arg_value": {
                                "type": "integer",
                                "description": "The test value.",
                            }
                        },
                        "required": ["arg_value"],
                    },
                )
            ],
        )
        assert ret.tool_calls[0].type == "function"
        assert ret.tool_calls[0].function.name == "test"
        assert ret.tool_calls[0].function.arguments == '{"arg_value":1}'
    finally:
        enable_llm_caching()
