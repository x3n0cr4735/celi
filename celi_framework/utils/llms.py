"""
The `utils.llms` module is designed to facilitate communication with Large Language Models (LLMs)
such as OpenAI's GPT models. It provides utility functions that abstract away the complexities
of sending prompts to the model, receiving responses, and handling various edge cases like
rate limits or excessive context lengths. This module is particularly useful for applications
that require robust and efficient interaction with LLMs for generating text, parsing information,
or conducting analysis based on model responses.

Features and Functionalities:
    - `ask_split` and `quick_ask`: Core functions for sending prompts to OpenAI's API, with built-in
        token counting, retries on failure, and verbose logging. `ask_split` is designed for more complex
        interactions involving system messages and user prompts, while `quick_ask` offers a streamlined
        approach for simple prompt-response cycles.
    - Token Counter Decorators: Decorators that wrap around the core functions to enforce token limits,
        ensuring that each query adheres to predefined constraints to manage costs and API usage efficiently.
    - Custom Error Handling: Implements error handling mechanisms to gracefully recover from common
        issues such as network timeouts, API rate limits, and context length exceedance. The
        `ContextLengthExceededException` specifically addresses scenarios where the prompt exceeds
        the maximum allowed context length, enabling the application to respond appropriately.
    - Memory Tracking: Utilizes the `tracemalloc` library to monitor memory allocation and identify
        potential inefficiencies, which is critical for applications processing large volumes of text
        or managing numerous concurrent interactions with the LLM.

"""

import asyncio
import logging
import random
import re
import time
from typing import Optional, Dict, List, Any, Tuple

import anthropic
import openai
from anthropic import RateLimitError as AnthropicRateLimitError
from openai import RateLimitError as OpenAIRateLimitError
from openai.types.chat import ChatCompletion
from pydantic import BaseModel, ValidationError
from requests import HTTPError
from botocore.exceptions import ClientError

from celi_framework.utils.anthropic_client import (
    anthropic_chat_completion,
    anthropic_bedrock_chat_completion,
)
from celi_framework.utils.converse_client import converse_bedrock_chat_completion
from celi_framework.utils.llm_cache import get_celi_llm_cache
from celi_framework.utils.llm_response import LLMResponse
from celi_framework.utils.log import app_logger
from celi_framework.utils.openai_client import (
    openai_chat_completion,
    llm_response_from_chat_completion,
)
from celi_framework.utils.token_counters import TokenCounter

logger = logging.getLogger(__name__)


class ToolDescription(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


async def ask_split(
    user_prompt: str | List[Tuple[str, str]],
    system_message,
    model_name,
    max_tokens=0,
    seed=777,
    verbose=False,  # model_name="gpt-4-1106-preview"
    max_retries=7,
    wait_between_retries=2,
    temperature=0.0,
    timeout: Optional[int] = 120,
    tool_descriptions: Optional[List[ToolDescription]] = None,
    model_url: Optional[str] = None,
    json_mode: bool = False,
    response_format = None,
    token_counter: Optional[TokenCounter] = None,
    force_tool_use: bool = False,
):
    """
    Sends a prompt to the OpenAI API and returns the response, with retries on error.

    user_prompt can be either a string or a list of messages.
    """
    err_cnt = 0
    last_error = None
    app_logger.info(f"Calling LLM {model_name}", extra={"color": "yellow"})
    defaulted_max_tokens = max_tokens if max_tokens != 0 else None
    while err_cnt < max_retries:
        try:
            if err_cnt > 1:
                app_logger.warning(f"Attempt {err_cnt + 1}:")
            tool_choice = (
                None
                if tool_descriptions is None
                else "required" if force_tool_use else "auto"
            )
            if json_mode:
                response_format = {"type": "json_object"}
            chat_completion = await cached_chat_completion(
                token_counter=token_counter,
                base_url=model_url,
                messages=[
                    {"role": "system", "content": system_message},
                ]
                + assemble_chat_messages(user_prompt),
                tools=(
                    [
                        {"type": "function", "function": _.model_dump()}
                        for _ in tool_descriptions
                    ]
                    if tool_descriptions
                    else None
                ),
                tool_choice=tool_choice,
                response_format=response_format,
                model=model_name,
                temperature=temperature,
                max_tokens=defaulted_max_tokens,
                seed=seed,
                timeout=timeout,
            )

            if verbose:
                app_logger.info(
                    f"LLM {model_name.upper()} responded", extra={"color": "yellow"}
                )
            return chat_completion

        except (
            openai.APIError,
            anthropic.BadRequestError,
            HTTPError,
            ConnectionError,
            TimeoutError,
        ) as e:
            err_cnt += 1
            app_logger.exception(f"Error attempt {err_cnt}")
            app_logger.warning(f"Error: Prompt was {user_prompt}")
            time.sleep(wait_between_retries)
            last_error = e

    if verbose:
        app_logger.error(f"All retries failed after {max_retries} attempts.")
    raise last_error  # type: ignore


def quick_ask(
    prompt,
    model_name,
    max_tokens=None,
    temperature=None,
    seed=777,
    verbose=False,
    json_output=False,  # model_name="gpt-4-1106-preview"
    response_format=None,
    max_retries=3,
    wait_between_retries=10,
    timeout=90,
    time_increase=30,
    model_url: Optional[str] = None,
    token_counter: Optional[TokenCounter] = None,
):
    return asyncio.run(
        quick_ask_async(
            prompt,
            model_name,
            max_tokens,
            temperature,
            seed,
            verbose,
            json_output,
            response_format,
            max_retries,
            wait_between_retries,
            timeout,
            time_increase,
            model_url,
            token_counter,
        )
    )


async def quick_ask_async(
    prompt,
    model_name,
    max_tokens=None,
    temperature=None,
    seed=777,
    verbose=False,
    json_output=False,  # model_name="gpt-4-1106-preview"
    response_format=None,
    max_retries=3,
    wait_between_retries=10,
    timeout=90,
    time_increase=30,
    model_url: Optional[str] = None,
    token_counter: Optional[TokenCounter] = None,
):
    """
    Simplified version of ask_split for quickly sending prompts to the OpenAI API, with error handling and retries.

    Args:
        prompt (str): The user's prompt to send to the model.
        model_name (str): Name of the GPT model to use.
        max_tokens (int, optional): Maximum number of tokens to generate.
        seed (int, optional): Seed for random number generation in the model.
        verbose (bool, optional): If True, prints additional information.
        json_output (bool, optional): If True, response will be in JSON format.
        max_retries (int, optional): Maximum number of retries on error.
        wait_between_retries (int, optional): Time in seconds to wait between retries.

    Returns:
        str: The content of the response message or error message after all retries.
    """
    err_cnt = 0
    last_error = None

    while err_cnt < max_retries:
        try:
            if err_cnt > 1:
                app_logger.warning(f"Attempt {err_cnt + 1}:")
            if verbose:
                app_logger.info(
                    f"Calling: {model_name.upper()}", extra={"color": "yellow"}
                )

            if json_output:
                if response_format:
                    app_logger.warning(f"A value has been provided for response_format (OpenAI Structured Outputs) while json_output (OpenAI JSON mode) is 'True'. The model will default to Structured Outputs. To use JSON mode, do not provide a value for response_format.")
                else:
                    response_format = {"type": "json_object"}

            chat_completion = await cached_chat_completion(
                token_counter=token_counter,
                base_url=model_url,
                messages=assemble_chat_messages(prompt),
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                seed=seed,
                response_format=response_format,
                timeout=timeout,
            )
            response = chat_completion.content

            if verbose:
                app_logger.info(
                    f"{model_name.upper()} responded", extra={"color": "yellow"}
                )

            return response
        except Exception as e:
            err_cnt += 1
            last_error = str(e)

            # Check for context length exceeded error in the exception message
            if (
                "context_length_exceeded" in last_error
                or "maximum context length" in last_error
            ):
                # If the specific error condition is met, raise a custom exception
                raise ContextLengthExceededException(last_error)

            app_logger.exception(f"Error: attempt {err_cnt}", extra={"color": "red"})
            app_logger.error(f"Error: Prompt was {prompt}")
            await asyncio.sleep(wait_between_retries)
            if timeout and time_increase:
                timeout += time_increase  # Note: Adjusting timeout may not affect the API call's internal timeout handling.
                wait_between_retries += time_increase

    if err_cnt >= max_retries:
        err = f"All retries failed after {max_retries} attempts."
        app_logger.error(err, extra={"color": "red"})
        # Instead of returning the error, consider raising a generic exception if recovery is not possible
        raise Exception(f"{err}\nLast error: {last_error} with Prompt:\n{prompt}")


VALID_ROLES = r"^[a-zA-Z0-9_-]+$"


def assemble_chat_messages(prompt: str | List[Tuple[str, str] | Dict[str, str]]):
    """Takes a prompt and formats it as chat messages.  Prompt can be in the form:
    * "" - str - A single prompt string
    * A list of ("role","content") tuples
    * A list of dictionaries of chat messages {"role":"assistant","content":"..."}
    """

    def format_message(m):
        if isinstance(m, dict):
            assert re.match(VALID_ROLES, m["role"]), f"Invalid role: {m['role']}"
            return m
        else:
            role = m[0]
            assert re.match(VALID_ROLES, role), f"Invalid role: {role}"
            return {"role": m[0], "content": m[1]}

    if isinstance(prompt, str):
        return [{"role": "user", "content": prompt}]
    else:
        return [format_message(msg) for msg in prompt]


async def cached_chat_completion(
    token_counter: Optional[TokenCounter] = None,
    base_url: Optional[str] = None,
    **kwargs,
):
    cache = get_celi_llm_cache()
    if cache:
        url_dict = {} if base_url is None else {"base_url": base_url}
        cache_args = {**url_dict, **kwargs}
        ret = await cache.check_llm_cache(**cache_args)
        if ret:
            app_logger.debug("Using cached LLM response")
            try:
                result = LLMResponse.model_validate(ret["completion"])
            except ValidationError as e:
                # Older caches can still have direct OpenAI responses cached instead of LLMResult objects.
                # This provides backwards compatibility with those cache entries.
                try:
                    resp = ChatCompletion.model_validate(ret["completion"])
                    result = llm_response_from_chat_completion(resp)
                except ValidationError as e2:
                    raise e2
            if token_counter:
                token_counter.count_cached_tokens(
                    kwargs.get("messages", ""),
                    kwargs.get("tools", ""),
                    result.content,
                )
            return result
        else:
            app_logger.debug("Caching LLM response")
            result = await create_chat_completion_with_retry(base_url, **kwargs)
            if token_counter:
                token_counter.count_request_tokens(
                    kwargs.get("messages", ""), kwargs.get("tools", "")
                )
            await cache.cache_llm_response(
                response={"completion": result.dict()}, **cache_args
            )
            if token_counter:
                token_counter.count_response_tokens(result.content)
            return result
    else:
        if token_counter:
            token_counter.count_request_tokens(
                kwargs.get("messages", ""), kwargs.get("tools", "")
            )
        result = await create_chat_completion_with_retry(base_url=base_url, **kwargs)
        if token_counter:
            token_counter.count_response_tokens(result.content)
        return result


class ContextLengthExceededException(Exception):
    """Exception raised when the input exceeds the model's maximum context length."""

    def __init__(self, message="Context length exceeded the model's maximum limit."):
        self.message = message
        super().__init__(self.message)


async def create_chat_completion_with_retry(base_url, **kwargs):
    max_retries = 5
    backoff_factor = 2
    retry_attempts = 0

    while True:
        try:
            return await call_client(base_url=base_url, **kwargs)
        except (AnthropicRateLimitError, OpenAIRateLimitError) as e:
            retry_attempts += 1
            if retry_attempts > max_retries:
                raise e
            sleep_time = 60 + 20 * random.uniform(0, 1) * backoff_factor**retry_attempts
            logger.warning(
                f"Rate limit exceeded. Retrying in {sleep_time:.2f} seconds..."
            )
        except ClientError as e:
            if e.response['Error']['Code'] == "ThrottlingException":
                retry_attempts += 1
                if retry_attempts > max_retries:
                    raise e
                sleep_time = 5 + random.uniform(1, 2) * backoff_factor**retry_attempts
                #sleep_time = 1 + random.uniform(1, 2) * backoff_factor**retry_attempts
                logger.warning(
                    f"Rate limit exceeded. Retrying in {sleep_time:.2f} seconds..."
                )
            else:
                raise e
        await asyncio.sleep(sleep_time)


async def call_client(base_url: Optional[str], **kwargs):
    model = kwargs.get("model", None)
    if model and model.startswith("claude"):
        assert (
            not base_url
        ), f"Changing the model URL is not supported for claude models.  {base_url}"
        return await anthropic_chat_completion(**kwargs)
    elif model and model.startswith("anthropic"):
        assert (
            not base_url
        ), f"Changing the model URL is not supported for claude models.  {base_url}"
        return await anthropic_bedrock_chat_completion(**kwargs)
    elif model and not model.startswith("gpt") and not model.startswith("chatgpt") and not model.startswith("o1"):
        assert (
            not base_url
        ), f"Changing the model URL is not supported for Bedrock models.  {base_url}"
        return await converse_bedrock_chat_completion(**kwargs)
    else:
        # Tools are not yet implemented for vLLM models.
        if base_url is not None:
            kwargs = {k: v for k, v in kwargs if k not in ["tools", "tool_choice"]}
        return await openai_chat_completion(base_url=base_url, **kwargs)
