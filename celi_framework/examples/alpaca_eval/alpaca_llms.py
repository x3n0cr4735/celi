import os

import openai
import logging
import json
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class MongoDBUtilitySingleton:
    #### Placeholder for MongoDB utility singleton class
    pass

class ContextLengthExceededException(Exception):
    pass

#### Setting up the OpenAI API client
def get_openai_client():
    return openai.OpenAI(api_key="skn")

def quick_ask(
    prompt: str,
    token_counter: Optional[Any],
    model_name: str,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    seed: int = 777,
    verbose: bool = False,
    json_output: bool = False,
    max_retries: int = 3,
    wait_between_retries: int = 10,
    timeout: int = 90,
    time_increase: int = 30,
    codex: Optional[MongoDBUtilitySingleton] = None,
) -> str:
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
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING)

    if token_counter is None:
        logger.error("global_token_counter inside quick_ask definition is None")

    def assemble_chat_messages(prompt: str) -> Dict[str, Any]:
        return [{"role": "user", "content": prompt}]

    chat_completion = get_openai_client().chat.completions.create(
        #### codex=codex,
        messages=assemble_chat_messages(prompt),
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        seed=seed,
        response_format={"type": "json_object"} if json_output else None,
        timeout=timeout,
    )

    response = chat_completion.choices[0].message.content
    #response = chat_completion.choices[0]



    return response