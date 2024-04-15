"""
The `utils.token_counters` module provides a set of tools for counting and managing tokens in text strings.
This is particularly useful for applications interfacing with language models like GPT-4, where understanding
and monitoring token usage is crucial for optimizing API calls and managing computational resources efficiently.

Key Components:
- `token_counter_og`: A function that returns the exact number of tokens in a text string for a specified API,
  using the `tiktoken` library for encoding. It's designed for cases where accuracy is paramount.
- `token_counter_est`: Provides a quick estimation of token count based on word count, using a heuristic approach.
  This function is useful for scenarios where performance is a consideration, and an exact token count is less critical.
- `TokenCounter`: A singleton class that tracks the number of tokens in requests and responses. It supports
  multiple instances (e.g., 'master', 'monitor') for different monitoring purposes within the same application,
  ensuring that only one instance of each type is created.
- `get_master_counter_instance` and `get_monitor_counter_instance`: Factory functions that return singleton instances
  of the `TokenCounter` class for specific purposes ('master' and 'monitor', respectively), ensuring application-wide
  consistency in token counting.
- `token_counter_decorator_ask_split` and `token_counter_decorator_quick_ask`: Decorators designed to wrap API call
  functions, counting tokens in both the request and response phases. These are particularly useful for integrating
  token counting into existing API interactions, providing a seamless way to monitor and manage token usage.

Usage:
This module is intended to be used in applications that require detailed monitoring and management of token usage,
especially when interfacing with language models. It provides both precise and estimated token counting functions,
along with a mechanism to track token usage throughout the application lifecycle via the `TokenCounter` class and
its singleton instances. The decorators offer a convenient way to add token counting to API calls without significant
modification to existing code.

Example:
```python
from utils.token_counters import get_master_counter_instance, token_counter_decorator_quick_ask

# Retrieve the master token counter instance
master_counter = get_master_counter_instance()

# Example API call function
@api_call_function
def fetch_data(api_endpoint, data):
    # Simulated API call logic
    return "Simulated response"

# Wrap the API call function with token counting
fetch_data_decorated = token_counter_decorator_quick_ask(fetch_data)

# Use the decorated function as normal
response = fetch_data_decorated(api_endpoint="http://example.com/api", data={"query": "example"}, token_counter=master_counter)
'''

This module is a comprehensive solution for managing token usage, crucial for optimizing interactions with language models and other token-based APIs.
"""

import functools
import tiktoken
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


# utils/token_counter.py


class TokenCounter:
    """Singleton class for counting tokens in requests and responses.

    This class is designed as a singleton to ensure that only one instance of each counter type exists within the application.
    It allows for tracking the number of tokens in requests and responses, supporting multiple counter types.

    Attributes:
        counter_type (str): A label for the counter instance, defaulting to 'general'.
        request_tokens (int): The total count of tokens in requests.
        response_tokens (int): The total count of tokens in responses.
    """

    _instances = {}  # Class level dictionary to hold instances

    def __new__(cls, counter_type="general"):
        if counter_type not in cls._instances:
            cls._instances[counter_type] = super(TokenCounter, cls).__new__(cls)
            app_logger.info(
                f"Initialized Global Token Counter: {counter_type}",
                extra={"color": "dark_grey"},
            )
        return cls._instances[counter_type]

    def __init__(self, counter_type="general"):
        self.counter_type = counter_type
        self.request_tokens = 0
        self.response_tokens = 0

    def count_tokens(self, message, is_response=False):
        try:
            # logger.info(f"Trying to run count_tokens", extra={'color': 'gray'})
            count = token_counter_og(message)
            if is_response:
                self.response_tokens += count
            else:
                self.request_tokens += count
        except Exception as e:
            app_logger.error(e)

    def get_total_tokens(self):
        return self.request_tokens, self.response_tokens


def get_master_counter_instance():
    """Retrieve or create the singleton instance of the TokenCounter for the master counter.

    This function ensures that there is only one 'master' instance of the TokenCounter being used
    throughout the application, following the Singleton design pattern.

    Returns:
        TokenCounter: The singleton instance of the master TokenCounter.
    """
    token_counter = TokenCounter(counter_type="master")
    return token_counter


def get_monitor_counter_instance():
    """Retrieve or create the singleton instance of the TokenCounter for the monitor counter.

    This function ensures that there is only one 'monitor' instance of the TokenCounter being used
    throughout the application, adhering to the Singleton design pattern. This specific instance
    can be used for monitoring purposes, separate from the master counter.

    Returns:
        TokenCounter: The singleton instance of the monitor TokenCounter.
    """
    token_counter = TokenCounter(counter_type="monitor")
    return token_counter


def token_counter_decorator_ask_split(api_call_function):
    """Decorator to count tokens before and after an API call within an ask_split scenario.

    This decorator wraps an API call function, counts the tokens in both the user prompt and the system message
    before making the call, and counts the tokens in the response after the call. This is particularly useful
    for operations that involve splitting user queries and system responses, ensuring accurate token tracking.

    Args:
        api_call_function (callable): The API call function to be decorated.

    Returns:
        callable: The wrapper function that enhances the original API call function with token counting.
    """

    @functools.wraps(api_call_function)
    def wrapper(*args, **kwargs):
        # Assume the token counter instance is passed as an argument
        dec_token_counter = kwargs.get("token_counter")
        if not dec_token_counter:
            app_logger.info(
                f"Token counter in decorator is None: {dec_token_counter}",
                extra={"color": "red"},
            )
            return api_call_function(
                *args, **kwargs
            )  # Proceed with the call without token counting

        user_prompt = kwargs.get("user_prompt") or args[1]
        system_message = kwargs.get("system_message", "")

        # Count tokens in the request
        dec_token_counter.count_tokens(system_message)
        dec_token_counter.count_tokens(user_prompt)

        # Make the API call
        # logger.info(f"Token_decorator - Trying to run api_call", extra={'color': 'gray'})
        response = api_call_function(*args, **kwargs)
        # logger.info(f"Token_decorator - Response received api_call", extra={'color': 'gray'})

        # For ask_split the response is choices[0] dict, and not the message, so let's handle that
        if type(response) != str and response is not None:
            response_txt = response.message.content
        else:
            response_txt = response

        # Count tokens in the response
        if response_txt:
            dec_token_counter.count_tokens(response_txt, is_response=True)

        # logger.info(f"Token_decorator - Response text which was counted: {response_txt}", extra={'color': 'gray'})
        # logger.info(f"Token_decorator - Response received and to be returned: {response}", extra={'color': 'gray'})
        return response

    return wrapper


def token_counter_decorator_quick_ask(api_call_function):
    """Decorator to count tokens before and after making a quick API call.

    This decorator is designed to quickly count the tokens in the prompt before making an API call and
    in the response after the call. It's streamlined for scenarios where prompt and response token counting
    is essential but must be done with minimal overhead.

    Args:
        api_call_function (callable): The API call function to be decorated.

    Returns:
        callable: The wrapper function that adds token counting functionality to the original API call function.
    """

    @functools.wraps(api_call_function)
    def wrapper(*args, **kwargs):
        token_counter = kwargs.get("token_counter")
        if not token_counter:
            return api_call_function(*args, **kwargs)  # Proceed without token counting

        prompt = kwargs.get("prompt") or args[0]

        token_counter.count_tokens(prompt)

        response = api_call_function(*args, **kwargs)

        if isinstance(response, str):
            token_counter.count_tokens(response, is_response=True)

        return response

    return wrapper
