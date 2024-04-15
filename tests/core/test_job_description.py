from typing import List

from celi_framework.core.job_description import (
    ToolImplementations,
    generate_tool_description,
    generate_tool_descriptions,
)
from celi_framework.utils.llms import ToolDescription


def example_function(ids: List[str]) -> List[str]:
    return ids


def test_generate_tool_description_list():
    td = generate_tool_description(example_function)
    expected = ToolDescription(
        name="example_function",
        description="",
        parameters={
            "type": "object",
            "properties": {
                "ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "No description provided.",
                }
            },
            "required": ["ids"],
        },
    )
    assert td == expected


class ExampleToolImplementations:
    def _private(self):
        pass

    def public(self, input: str) -> str:
        return input

    def __hidden__(self):
        pass


def test_generate_tool_descriptions_skip_private():
    td = generate_tool_descriptions(ExampleToolImplementations)
    expected = ToolDescription(
        name="public",
        description="",
        parameters={
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "No description provided.",
                }
            },
            "required": ["input"],
        },
    )
    assert td == [expected]
