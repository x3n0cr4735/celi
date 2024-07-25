"""
The `utils.token_counters` module provides a set of tools for counting and managing tokens in text strings.
This is particularly useful for applications interfacing with language models like GPT-4, where understanding
and monitoring token usage is crucial for optimizing API calls and managing computational resources efficiently.

Key Components:
    - `token_counter_og`: A function that returns the exact number of tokens in a text string for a specified API,
        using the `tiktoken` library for encoding. It's designed for cases where accuracy is paramount.
    - `token_counter_est`: Provides a quick estimation of token count based on word count, using a heuristic approach.
        This function is useful for scenarios where performance is a consideration, and an exact token count is less critical.
    - `TokenCounter`: A class that tracks the number of tokens in requests and responses.

Usage:
This module is intended to be used in applications that require detailed monitoring and management of token usage,
especially when interfacing with language models. It provides both precise and estimated token counting functions,
along with a mechanism to track token usage throughout the application lifecycle via the `TokenCounter` class and
its singleton instances. The decorators offer a convenient way to add token counting to API calls without significant
modification to existing code.
"""

from dataclasses import dataclass, field
from typing import Callable

from celi_framework.utils.log import app_logger


def token_counter_og(string, api="gpt-4") -> int:
    """Returns the exact number of tokens in a text string for a specified API.

    This function encodes a string using the tiktoken library's encoding functionality,
    specifically tailored to the GPT-4 model, or logs an error if an unsupported API is specified.

    Args:
        string (str): The text string to encode.
        api (str): The API specification, defaulting to 'gpt-4'.

    Returns:
        int: The number of tokens in the encoded string.
    """
    if api == "gpt-4":
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(string, disallowed_special=()))
    else:
        app_logger.error("API not set correctly for tiktoken")
    return num_tokens


def token_counter_est(string: str) -> int:
    """Returns an estimated number of tokens in a text string based on word count.

    This function provides a quick estimation of token count by multiplying the word count by 4/3,
    a heuristic for approximating tokens in typical English text.

    Args:
        string (str): The text string to estimate token count for.

    Returns:
        int: The estimated number of tokens.
    """
    word_count = len(string.split())
    estimated_tokens = int(word_count * 4 / 3)  # Multiply by 4/3 to approximate tokens
    return estimated_tokens


@dataclass
class TokenCounter:
    """Counts tokens in requests and responses and applies an optional budget."""

    token_budget: int = 0
    token_counter_fn: Callable[[str], int] = token_counter_est

    current_token_count: int = field(default=0, init=False)
    cached_token_count: int = field(default=0, init=False)

    def count_request_tokens(self, *prompt_fields):
        """Counts request tokens by converting all prompt_fields to strings and raises an exception if it exceeded the budget."""
        self.current_token_count += sum(
            self.token_counter_fn(str(_)) for _ in prompt_fields
        )
        if self.token_budget and self.current_token_count > self.token_budget:
            raise ValueError(
                f"LLM Token budget exceeded.  Budget was {self.token_budget}. Consumed {self.current_token_count} tokens and {self.cached_token_count} cached tokens."
            )

    def count_response_tokens(self, response: str | None):
        self.current_token_count += self.token_counter_fn(str(response))

    def count_cached_tokens(self, *prompt_fields):
        self.cached_token_count += sum(
            self.token_counter_fn(str(_)) for _ in prompt_fields
        )
