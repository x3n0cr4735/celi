import logging

import pytest
from anthropic.types import Message, TextBlock, ToolUseBlock, Usage

from celi_framework.utils.anthropic_client import (
    anthropic_chat_completion,
    _convert_openai_to_anthropic_input,
    _parse_anthropic_response,
)
from celi_framework.utils.llm_cache import disable_llm_caching, enable_llm_caching
from celi_framework.utils.llm_response import LLMResponse, ToolCall, FunctionCall
from celi_framework.utils.llms import ToolDescription, ask_split

logger = logging.getLogger(__name__)


@pytest.mark.skip
@pytest.mark.asyncio
async def test_anthropic_chat_completion():
    ret = await anthropic_chat_completion(
        messages=[{"role": "user", "content": "the quick brown fox jumps over the"}],
        model="claude-2.1",
        max_tokens=10,
    )
    logger.info(f"LLM returned: {ret}")


def test_adjust_args_for_anthropic():
    tool_description = ToolDescription(
        name="complete_section",
        description="It will empty out the current chat history.",
        parameters={
            "type": "object",
            "properties": {
                "current_section_number": {
                    "type": "string",
                    "description": "Current taskID.",
                }
            },
            "required": ["current_section_number"],
        },
    )

    def make_args():
        return {
            "messages": [
                {"role": "system", "content": "instructions"},
                {"role": "user", "content": "real prompt"},
            ],
            "response_format": "json",
            "tool_choice": "auto",
            "max_tokens": 10,
            "tools": [{"type": "function", "function": tool_description.model_dump()}],
        }

    input_args = make_args()
    actual = _convert_openai_to_anthropic_input(**input_args)
    assert input_args == make_args(), "Input was altered"
    assert actual == {
        "messages": [{"role": "user", "content": "real prompt"}],
        "system": "instructions",
        "tool_choice": {"type": "auto"},
        "max_tokens": 10,
        "tools": [
            {
                "description": "It will empty out the current chat history.",
                "name": "complete_section",
                "input_schema": {
                    "properties": {
                        "current_section_number": {
                            "description": "Current " "taskID.",
                            "type": "string",
                        }
                    },
                    "required": ["current_section_number"],
                    "type": "object",
                },
            }
        ],
    }


def test_filter_empty_text():
    def make_args():
        return {
            "messages": [
                {"role": "user", "content": "real prompt"},
                {"role": "assistant", "content": ""},
                {"role": "user", "content": "try again"},
                {"role": "assistant", "content": "ok"},
                {"role": "user", "content": "better"},
            ],
            "max_tokens": None,
        }

    input_args = make_args()
    actual = _convert_openai_to_anthropic_input(**input_args)
    assert input_args == make_args(), "Input was altered"
    assert actual == {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": "real prompt", "type": "text"},
                    {"text": "try again", "type": "text"},
                ],
            },
            {
                "role": "assistant",
                "content": "ok",
            },
            {"role": "user", "content": "better"},
        ],
        "max_tokens": 4096,
    }


def test_adjust_dedup_user():
    def make_args():
        return {
            "messages": [
                {"role": "user", "content": "instructions"},
                {"role": "user", "content": "real prompt"},
                {"role": "assistant", "content": "result"},
                {
                    "role": "function",
                    "name": "get_prompt",
                    "id": "tool_id_42",
                    "arguments": '{"task_id": "HumanEval/9"}',
                    "return_value": "function_return",
                    "is_error": False,
                },
            ],
            "max_tokens": None,
        }

    input_args = make_args()
    actual = _convert_openai_to_anthropic_input(**input_args)
    assert input_args == make_args(), "Input was altered"
    assert actual == {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": "instructions", "type": "text"},
                    {"text": "real prompt", "type": "text"},
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {"text": "result", "type": "text"},
                    {
                        "id": "tool_id_42",
                        "input": {"task_id": "HumanEval/9"},
                        "name": "get_prompt",
                        "type": "tool_use",
                    },
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "content": "function_return",
                        "tool_use_id": "tool_id_42",
                        "type": "tool_result",
                        "is_error": False,
                    }
                ],
            },
        ],
        "max_tokens": 4096,
    }


def test_adjust_multiple_tool_calls():
    def make_args():
        return {
            "messages": [
                {"role": "user", "content": "real prompt"},
                {"role": "assistant", "content": "result"},
                {
                    "role": "function",
                    "name": "get_prompt",
                    "id": "tool_id_42",
                    "arguments": '{"task_id": "HumanEval/9"}',
                    "return_value": "function_return",
                    "is_error": False,
                },
                {
                    "role": "function",
                    "name": "get_prompt",
                    "id": "tool_id_43",
                    "arguments": '{"task_id": "HumanEval/10"}',
                    "return_value": "function_return",
                    "is_error": False,
                },
            ],
            "max_tokens": None,
        }

    input_args = make_args()
    actual = _convert_openai_to_anthropic_input(**input_args)
    assert input_args == make_args(), "Input was altered"
    assert actual == {
        "messages": [
            {
                "role": "user",
                "content": "real prompt",
            },
            {
                "role": "assistant",
                "content": [
                    {"text": "result", "type": "text"},
                    {
                        "id": "tool_id_42",
                        "input": {"task_id": "HumanEval/9"},
                        "name": "get_prompt",
                        "type": "tool_use",
                    },
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "content": "function_return",
                        "tool_use_id": "tool_id_42",
                        "type": "tool_result",
                        "is_error": False,
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "id": "tool_id_43",
                        "input": {"task_id": "HumanEval/10"},
                        "name": "get_prompt",
                        "type": "tool_use",
                    },
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "content": "function_return",
                        "tool_use_id": "tool_id_43",
                        "type": "tool_result",
                        "is_error": False,
                    }
                ],
            },
        ],
        "max_tokens": 4096,
    }


def test_assistant_final():
    def make_args():
        return {
            "messages": [
                {"role": "user", "content": "instructions"},
                {"role": "assistant", "content": "previous response"},
            ],
            "max_tokens": None,
        }

    input_args = make_args()
    actual = _convert_openai_to_anthropic_input(**input_args)
    assert input_args == make_args(), "Input was altered"
    assert actual == {
        "messages": [
            {"role": "user", "content": "instructions"},
            {"role": "assistant", "content": "previous response"},
            {
                "role": "user",
                "content": "Think step by step and then make the tool call you need to accomplish the task.",
            },
        ],
        "max_tokens": 4096,
    }


def test_no_tools():
    def make_args():
        return {
            "messages": [
                {"role": "user", "content": "instructions"},
            ],
            "tools": None,
            "tool_choice": "auto",
            "max_tokens": None,
        }

    input_args = make_args()
    actual = _convert_openai_to_anthropic_input(**input_args)
    assert input_args == make_args(), "Input was altered"
    assert actual == {
        "messages": [
            {"role": "user", "content": "instructions"},
        ],
        "max_tokens": 4096,
    }


def test_parse_anthropic_response():
    m = Message(
        id="msg_01WbHHXnfgbWikz4DRaGfi68",
        content=[
            TextBlock(
                text="Certainly! I'll proceed to document section HumanEval/9",
                type="text",
            ),
            ToolUseBlock(
                id="toolu_01Rd9Mhfd7RecdBmBWjMzMco",
                input={"task_id": "HumanEval/9"},
                name="get_prompt",
                type="tool_use",
            ),
        ],
        model="claude-3-5-sonnet-20240620",
        role="assistant",
        stop_reason="tool_use",
        stop_sequence=None,
        type="message",
        usage=Usage(input_tokens=2041, output_tokens=130),
    )
    actual = _parse_anthropic_response(m)
    assert actual == LLMResponse(
        content="Certainly! I'll proceed to document section HumanEval/9",
        finish_reason="tool_calls",
        tool_calls=[
            ToolCall(
                id="toolu_01Rd9Mhfd7RecdBmBWjMzMco",
                type="function",
                function=FunctionCall(
                    name="get_prompt", arguments='{"task_id": "HumanEval/9"}'
                ),
            )
        ],
    )


@pytest.mark.skip
@pytest.mark.asyncio
async def test_ask_split_anthropic_with_tools():
    try:
        await disable_llm_caching()
        ret = await ask_split(
            "Please call the test tool with value 1",
            system_message="You are a test for tool calls",
            # model_name="anthropic.claude-3-sonnet-20240229-v1:0",
            model_name="claude-3-5-sonnet-20240620",
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
        assert (
            ret.tool_calls[0].function.arguments.replace(" ", "") == '{"arg_value":1}'
        )
    finally:
        enable_llm_caching()
