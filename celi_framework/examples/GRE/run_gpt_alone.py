import os

from dotenv import load_dotenv

from celi_framework.utils.llms import ask_split, quick_ask
from celi_framework.utils.utils import load_text_file, load_json
from celi_framework.examples.GRE.templates.templates import make_gpt_prompt, make_gpt_prompt_simple, score_llm_output

load_dotenv()

ROOT_DIR = os.getenv('ROOT_DIR')
CURRENT_QUESTIONS_DIR = f'{ROOT_DIR}/celi_framework/examples/GRE/data/working_data/targets'
EXAMPLE_QUESTIONS_DIR = f'{ROOT_DIR}/celi_framework/examples/GRE/data/working_data/examples'
schema = load_json(f"{ROOT_DIR}/celi_framework/examples/AP_English_Language/schema.json")

# for i in range(1, 2):
#     for key in schema.keys():

key='q1'

current_prompt = load_text_file(file_path=f'{CURRENT_QUESTIONS_DIR}/set_3_target_{key}_question.txt')

example_prompt = load_text_file(file_path=f'{EXAMPLE_QUESTIONS_DIR}/set_1_example_{key}_question.txt')
example_response = load_text_file(file_path=f'{EXAMPLE_QUESTIONS_DIR}/set_1_example_{key}_response.txt')

example_prompt_response = f"Prompt:\n{example_prompt}\n\n{example_response}"

system_message, user_prompt = make_gpt_prompt_simple(current_prompt=current_prompt,
                                                    example_prompt_response=example_prompt_response)

whole_prompt = f"{system_message}\n\n{user_prompt}"

print("Whole Prompt:")
print(f"{whole_prompt}")

# print(f"{whole_prompt}\n\n")
llm_response = quick_ask(prompt=whole_prompt, token_counter=None)

print(llm_response)

# TODO: Automate scoring using score_llm_output template


