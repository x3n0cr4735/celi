import os

from dotenv import load_dotenv

from celi_framework.utils.llms import ask_split, quick_ask
from celi_framework.utils.utils import load_text_file, load_json
from celi_framework.examples.AP_English_Language.templates.gpt_alone import (make_gpt_alone_prompt,
                                                                             make_gpt_alone_prompt_7_steps,
                                                                             make_gpt_alone_prompt_simplified)

load_dotenv()

ROOT_DIR = os.getenv('ROOT_DIR')
CURRENT_QUESTIONS_DIR = f'{ROOT_DIR}/celi_framework/examples/AP_English_Language/data/working_data/targets'
EXAMPLE_QUESTIONS_DIR = f'{ROOT_DIR}/celi_framework/examples/AP_English_Language/data/working_data/examples'
schema = load_json(f"{ROOT_DIR}/celi_framework/examples/AP_English_Language/schema.json")

for i in range(1, 4):
    for key in schema.keys():
        current_prompt = load_text_file(file_path=f'{CURRENT_QUESTIONS_DIR}/set_1_target_{key}_question.txt')

        # example_prompt = load_text_file(file_path=f'{EXAMPLE_QUESTIONS_DIR}/set_2_example_{key}_question.txt')
        example_response = load_text_file(file_path=f'{EXAMPLE_QUESTIONS_DIR}/set_2_example_{key}_response_a.txt')

        example_response = f"{example_response}"

        system_message, user_prompt = make_gpt_alone_prompt_simplified(current_prompt=current_prompt,
                                                            example_response=example_response)

        whole_prompt = f"{system_message}\n\n{user_prompt}"

        # print(f"{whole_prompt}\n\n")
        llm_response = quick_ask(prompt=whole_prompt, token_counter=None)

        print(llm_response)



