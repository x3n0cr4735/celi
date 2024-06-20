# TODO -> Put stuff in utils/common where it makes sense

from dotenv import load_dotenv

load_dotenv()

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from celi_framework.core.job_description import ToolImplementations
from celi_framework.utils.log import app_logger as logger
from celi_framework.utils.utils import load_json, load_text_file
from docx import Document

cur_dir = os.path.dirname(os.path.realpath(__file__))

# Adjust paths to reflect new JSON structure
ALL_QUESTIONS_DIR = f"{cur_dir}/data/working_data/instructions"
EXAMPLE_QUESTIONS_DIR = f"{cur_dir}/data/working_data/examples"

@dataclass
class AlpacaEvalToolImplementations(ToolImplementations):
    def __post_init__(self):
        self.schema = self.load_json(f"{cur_dir}/schema.json")

    # Utility method to load JSON files
    @staticmethod
    def load_json(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    # Retrieves the question numbers and topics of the questions that need to be answered.
    def get_schema(self) -> Dict[str, str]:
        return self.schema

    def get_rubric(self) -> str:
        """
        Retrieves the rubric to score the questions.

        Returns:
            str: The rubric to score the question.
        """
        rubric_file_path = f"{cur_dir}/data/working_data/rubric/gre_1_scoring_guidelines.txt"
        with open(rubric_file_path, 'r', encoding='utf-8') as file:
            rubric_data = file.read()
        return rubric_data

    def retrieve_question_prompt(self, question_number: str) -> str:
        """
        Retrieves the prompt for a given question in the free response section of the test.

        Args:
            question_number (str): The unique identifier for the question (q1, q2, or q3).

        Returns:
            str: The prompt for the question.
        """
        prompt_data = self.load_json(f"{ALL_QUESTIONS_DIR}/instructions_sample.json")
        print(prompt_data) 
        return prompt_data[question_number]['instruction']

    def retrieve_example_prompt_response(self, question_number: str) -> str:
        """
        Retrieves a prompt, answer pair for a question that tests similar skills as the question being answered in the free response section of the test.

        Args:
            question_number (str): The unique identifier for the question (q1).

        Returns:
            str: Prompt, question example pair.
        """
        example = self.load_json(f"{EXAMPLE_QUESTIONS_DIR}/set_1_example.json")
        prompt = example[question_number]['instruction']
        response = example[question_number]['output']
        pair = f"{prompt}\n\n{response}"
        return pair

    def save_json (self, response):
        
        # Specify the JSON output file path
        json_file_path = "output/gpt/alpaca_eval_auto_output.json"

        # Save the collected question-answer pairs to a JSON file
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=4)

        print("Responses have been auto saved to JSON.")

