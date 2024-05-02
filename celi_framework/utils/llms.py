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

import functools
import os
import time
from typing import Optional, Dict, List, Any, Tuple
from pydantic import BaseModel
import openai
from openai.types.chat import ChatCompletion
from requests import HTTPError
from dotenv import load_dotenv

from celi_framework.utils.codex import MongoDBUtilitySingleton
from celi_framework.utils.token_counters import (
    token_counter_decorator_ask_split,
    token_counter_decorator_quick_ask,
)
from celi_framework.utils.log import app_logger
from celi_framework.utils.exceptions import ContextLengthExceededException

load_dotenv()

ASK_SPLIT_MODEL_NAME = os.getenv("PROCESSOR_LLM_MODEL_NAME")
ASK_SPLIT_MODEL_TEMP=float(os.getenv("PROCESSOR_LLM_MODEL_TEMP"))

QUICK_ASK_MODEL_NAME=os.getenv("QUICK_ASK_LLM_MODEL_NAME")
QUICK_ASK_MODEL_TEMP=float(os.getenv("QUICK_ASK_LLM_MODEL_TEMP"))

# Initialize the OpenAI client, using the OPENAI_API_KEY environment variable.
@functools.lru_cache(1)
def get_openai_client():
    return openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])


class ToolDescription(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


@token_counter_decorator_ask_split  # TODO - Not necessary to run outside of project
def ask_split(
    user_prompt: str | List[Tuple[str, str]],
    system_message,
    model_name=ASK_SPLIT_MODEL_NAME,
    max_tokens=4096,
    seed=777,
    verbose=False,  # model_name="gpt-4-1106-preview"
    max_retries=7,
    wait_between_retries=2,
    temperature=0.0,
    timeout: Optional[int] = 120,
    codex: Optional[MongoDBUtilitySingleton] = None,
    tool_descriptions: List[ToolDescription] = [],
):
    """
    Sends a prompt to the OpenAI API and returns the response, with retries on error.

    user_prompt can be either a string or a list of messages.
    """
    err_cnt = 0
    last_error = None
    app_logger.info(f"Calling LLM {model_name.upper()}", extra={"color": "yellow"})
    while err_cnt < max_retries:
        try:
            if err_cnt > 1:
                app_logger.error(f"Attempt {err_cnt + 1}:", extra={"color": "red"})
            chat_completion = cached_chat_completion(
                codex=codex,
                messages=[
                    {"role": "system", "content": system_message},
                ]
                + assemble_chat_messages(user_prompt),
                tools=[
                    {"type": "function", "function": _.model_dump()}
                    for _ in tool_descriptions
                ],
                tool_choice="auto",
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                seed=seed,
                timeout=timeout,
            )
            if verbose:
                app_logger.info(
                    f"LLM {model_name.upper()} responded", extra={"color": "yellow"}
                )
            return chat_completion.choices[0]

        except (
            openai.RateLimitError,
            openai.APIError,
            HTTPError,
            ConnectionError,
            TimeoutError,
        ) as e:
            err_cnt += 1
            app_logger.exception(f"Error attempt {err_cnt}", extra={"color": "red"})
            time.sleep(wait_between_retries)
            last_error = e

    if verbose:
        app_logger.error(
            f"All retries failed after {max_retries} attempts.", extra={"color": "red"}
        )
    raise last_error  # type: ignore


@token_counter_decorator_quick_ask
def quick_ask(
    prompt,
    token_counter,
    model_name=QUICK_ASK_MODEL_NAME,
    temperature=QUICK_ASK_MODEL_TEMP,
    max_tokens=None,
    seed=777,
    verbose=False,
    json_output=False,  # model_name="gpt-4-1106-preview"
    max_retries=3,
    wait_between_retries=10,
    timeout=90,
    time_increase=30,
    codex: Optional[MongoDBUtilitySingleton] = None,
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
    if token_counter is None:
        app_logger.error(
            f"global_token_counter inside quick_ask definition is {token_counter}",
            extra={"color": "red"},
        )
    err_cnt = 0
    last_error = None

    # Assuming the beginning parts of the function are unchanged
    ...

    while err_cnt < max_retries:
        try:
            if err_cnt > 1:
                app_logger.error(f"Attempt {err_cnt + 1}:", extra={"color": "red"})
            if verbose:
                app_logger.info(
                    f"Calling: {model_name.upper()}", extra={"color": "yellow"}
                )

            if json_output:
                response_format = {"type": "json_object"}
            else:
                response_format = None

            chat_completion = cached_chat_completion(
                codex=codex,
                messages=assemble_chat_messages(prompt),
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                seed=seed,
                response_format=response_format,
                timeout=timeout,
            )

            response = chat_completion.choices[0].message.content

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
            time.sleep(wait_between_retries)
            if timeout and time_increase:
                timeout += time_increase  # Note: Adjusting timeout may not affect the API call's internal timeout handling.
                wait_between_retries += time_increase

    if err_cnt >= max_retries:
        err = f"All retries failed after {max_retries} attempts."
        app_logger.error(err, extra={"color": "red"})
        # Instead of returning the error, consider raising a generic exception if recovery is not possible
        raise Exception(f"{err}\nLast error: {last_error} with Prompt:\n{prompt}")


def assemble_chat_messages(prompt: str | List[Tuple[str, str] | Dict[str, str]]):
    """Takes a prompt and formats it as chat messages.  Prompt can be in the form:
    * "" - str - A single prompt string
    * A list of ("role","content") tuples
    * A list of dictionaries of chat messages {"role":"assistant","content":"..."}
    """

    def format_message(m):
        if isinstance(m, dict):
            return m
        else:
            return {"role": m[0], "content": m[1]}

    if isinstance(prompt, str):
        return [{"role": "user", "content": prompt}]
    else:
        return [format_message(msg) for msg in prompt]


def cached_chat_completion(
    codex: Optional[MongoDBUtilitySingleton], **kwargs
) -> ChatCompletion:
    if codex:
        ret = codex.check_llm_cache(**kwargs)
        if ret:
            app_logger.debug("Using cached LLM response")
            return ChatCompletion.model_validate(ret["completion"])
        else:
            app_logger.debug("Caching LLM response")
            result = get_openai_client().chat.completions.create(**kwargs)
            codex.cache_llm_response(response={"completion": result.dict()}, **kwargs)
            return result
    else:
        return get_openai_client().chat.completions.create(**kwargs)
