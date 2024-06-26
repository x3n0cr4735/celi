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
import textgrad as tg
from textgrad.tasks import load_task

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
        rubric_file_path = f"{cur_dir}/data/working_data/rubric/alpaca_2_scoring_guide.txt"
        with open(rubric_file_path, 'r', encoding='utf-8') as file:
            rubric_data = file.read()
        return rubric_data
    
    def retrieve_question_prompt(self, question_number: str) -> str:
        """
        Retrieves the prompt for a given question in the free response section of the test.
        Args:
        question_number (str): The string representation of the question number (e.g., "1", "2", "3").
        Returns:
        str: The prompt for the question.
        """
        prompt_data = self.load_json(f"{ALL_QUESTIONS_DIR}/instructions_sample.json")
        
        try:
            # Convert the string to a zero-based index
            index = int(question_number) - 1
            
            # Ensure index is within the valid range
            if index < 0 or index >= len(prompt_data):
                raise ValueError(f"Invalid question number: {question_number}. Must be between 1 and {len(prompt_data)}")
            
            return prompt_data[index]['instruction']
        except ValueError:
            raise ValueError(f"Invalid question number: {question_number}. Must be a valid integer string.")
        

    # def retrieve_question_prompt(self,question_number: str) -> str:
    #     """
    #     Retrieves the prompt for a given question in the free response section of the test.

    #     Args:
    #         question_number (str): The unique identifier for the question (q1, q2, or q3).

    #     Returns:
    #         str: The prompt for the question.
    #     """
    #     prompt_data = self.load_json(f"{ALL_QUESTIONS_DIR}/instructions_sample.json")
    #     #print(prompt_data) 
    #     return prompt_data[question_number]['instruction']

    # def retrieve_example_prompt_response(self) -> str:
    #     """
    #     Retrieves a prompt, answer pair for a question that tests similar skills as the question being answered in the free response section of the test.

    #     Args:
    #         question_number (str): The unique identifier for the question (q1).

    #     Returns:
    #         str: Prompt, question example pair.
    #     """
    #     example = self.load_json(f"{EXAMPLE_QUESTIONS_DIR}/set_1_example.json")
    #     prompt = example["1"]['instruction']
    #     response = example["1"]['output']
    #     pair = f"{prompt}\n\n{response}"
    #     return pair

    # def save_json(self, response, question_number):
    #     # Specify the JSON output file path
    #     json_file_path = os.path.join(cur_dir, "output/gpt/alpaca_eval_auto_output.json")
        
    #     print("#################Saving responses to JSON...")
    #     print("Initial Response:", response)

    #     # Load existing data or initialize an empty dictionary
    #     if os.path.exists(json_file_path):
    #         with open(json_file_path, 'r', encoding='utf-8') as file:
    #             try:
    #                 data = json.load(file)
    #             except json.JSONDecodeError:
    #                 print("Existing JSON file corrupted, initializing new data.")
    #                 data = {}
    #     else:
    #         data = {}

    #     # Ensure the response is a valid JSON string
    #     try:
    #         # Directly attempt to parse the response if already properly formatted
    #         if isinstance(response, str):
    #             response = json.loads(response)
    #     except json.JSONDecodeError:
    #         print("Failed to decode the JSON response. Check formatting.")
    #         # Attempt to fix common formatting issues and retry
    #         try:
    #             formatted_response = response.replace("'", '"').replace('\\\\', '\\')
    #             response = json.loads(formatted_response)
    #         except json.JSONDecodeError:
    #             print("Second decoding attempt failed. Formatted Response for Debug:", formatted_response)
    #             return

    #     # Append or create new entry for the question number
    #     data.setdefault(question_number, {}).update(response)

    #     # Save the updated data to the JSON file
    #     with open(json_file_path, 'w', encoding='utf-8') as file:
    #         json.dump(data, file, ensure_ascii=False, indent=4)

    #     print("Responses have been auto-saved to JSON under the question number:", question_number)
    
    
    ################## Save json from CL, has keys in the output
    # def save_json(self, response, question_number):
    #     # Specify the JSON output file path
    #     cur_dir = os.path.dirname(os.path.abspath(__file__))
    #     json_file_path = os.path.join(cur_dir, "output/gpt/alpaca_eval_auto_output.json")
    #     print("#################Saving responses to JSON...")
    #     print("Initial Response:", response)

    #     # Load existing data or initialize an empty dictionary
    #     if os.path.exists(json_file_path):
    #         with open(json_file_path, 'r', encoding='utf-8') as file:
    #             try:
    #                 data = json.load(file)
    #             except json.JSONDecodeError:
    #                 print("Existing JSON file corrupted, initializing new data.")
    #                 data = {}
    #     else:
    #         data = {}

    #     # Ensure the response is a valid JSON object
    #     if isinstance(response, str):
    #         try:
    #             response = json.loads(response)
    #         except json.JSONDecodeError:
    #             print("Failed to decode the JSON response. Using the string as is.")
    #             response = {"response": response}

    #     # Append or create new entry for the question number
    #     data[str(question_number)] = response

    #     # Save the updated data to the JSON file
    #     with open(json_file_path, 'w', encoding='utf-8') as file:
    #         json.dump(data, file, ensure_ascii=False, indent=4)
    #     print("Responses have been auto-saved to JSON under the question number:", question_number)
    

################## Save json from CL, has keys in the output

    def save_json(self, response, question_number):
        # Specify the JSON output file path
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(cur_dir, f"output/gpt/alpaca_eval_auto_output.json")
        
        print("#################Saving responses to JSON...")
        print("Initial Response:", response)
        
        # Load existing data or initialize an empty list
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    if not isinstance(data, list):
                        data = []
                except json.JSONDecodeError:
                    print("Existing JSON file corrupted, initializing new data.")
                    data = []
        else:
            data = []
        
        # Ensure the response is a valid JSON object
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError:
                print("Failed to decode the JSON response. Using the string as is.")
                response = {"response": response}
        
        # Rename 'final_response' to 'output' if it exists
        if 'final_response' in response:
            response['output'] = response.pop('final_response')
        
        # Append the response to the list
        data.append(response)
        
        # Save the updated data to the JSON file
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        print(f"Response has been auto-saved to JSON. Total entries: {len(data)}")

    def generate_system_prompt(self, current_question):
        '''This function uses text_grad to generate a prompt for each question'''

        instruction = current_question
        llm_engine = tg.get_engine("gpt-3.5-turbo")
        tg.set_backward_engine("gpt-4o",override=True)

        #_, val_set, _, eval_fn = load_task("BBH_object_counting", llm_engine)
        #question_str, answer_str = val_set[0]
        question = tg.Variable(instruction, role_description="question to the LLM", requires_grad=False)
        #answer = tg.Variable("This will have the exact answer for the question", role_description="answer to the question", requires_grad=False)
       
        system_prompt = tg.Variable("You are a concise LLM. Think step by step.",
                            requires_grad=True,
                            role_description="system prompt to guide the LLM's reasoning strategy for accurate responses")

        model = tg.BlackboxLLM(llm_engine, system_prompt=system_prompt)
        optimizer = tg.TGD(parameters=list(model.parameters()))

        prediction = model(question)
        
        evaluation_instruction = (f"Here's a question: {question}. " 
                           "Create a prompt that will guide the LLM to answer the question. "
                           "be smart, logical, and very critical. "
                           "Just provide concise feedback.")
        
        

        # TextLoss is a natural-language specified loss function that describes 
        # how we want to evaluate the reasoning.
        loss_fn = tg.TextLoss(evaluation_instruction)
        loss = loss_fn(prediction)
        for i in range(2):
            loss.backward()
            optimizer.step()
      
        prediction = model(question)
        return f"This is the helping prompt for the current question. {system_prompt}."
        
