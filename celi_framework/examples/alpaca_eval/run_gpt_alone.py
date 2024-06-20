import os

from docx import Document
from dotenv import load_dotenv
import ast
from alpaca_llms import quick_ask
from celi_framework.utils.utils import load_text_file, load_json_wo_utf8
from templates.templates import make_gpt_prompt_alpaca, make_gpt_prompt_alpaca_wit_grade,make_gpt_prompt_alpaca_wit_grade_COV,   score_llm_prompt
import json
import random

load_dotenv()

alpaca_dir = os.path.dirname(__file__)
ALL_QUESTIONS_DIR = f"{alpaca_dir}/data/working_data/instructions"
EXAMPLE_QUESTIONS_DIR = f"{alpaca_dir}/data/working_data/examples"
#EXAMPLE_RUBRIC_DIR = f"{alpaca_dir}/data/working_data/rubric"

#schema = load_json(f"{alpaca_dir}/../AP_English_Language/schema.json")

# for i in range(1, 2):
#     for key in schema.keys():

qa_pairs = []
def run_gpt():
    
        
    all_instructions = load_json_wo_utf8(
        file_path=f"{ALL_QUESTIONS_DIR}/instructions_all.json"
    )
    example_instructions = load_json_wo_utf8(
        file_path=f"{EXAMPLE_QUESTIONS_DIR}/set_1_example.json"
    )
    
    # Construct prompt string
    example_prompt_response  = "Examples for LLM training:\n"
    for entry in example_instructions:
        example_prompt_response  += f"Instruction: {entry['instruction']}\n Output: {entry['output']}\n\n"

    #print(example_prompt_response )
    sample_instructions = all_instructions[100:105]
    #sample_instructions = random.sample(all_instructions, 10)
    for index, entry in enumerate(sample_instructions):
        current_prompt = sample_instructions[index]["instruction"]
        
        #print(f"Question {index+1}: {current_prompt}")

 
        # example_rubric = load_text_file(
        #     file_path=f"{EXAMPLE_RUBRIC_DIR}/gre_1_scoring_guidelines.txt"
        # )


        system_message, user_prompt = make_gpt_prompt_alpaca_wit_grade_COV(
            current_instruction =current_prompt,
            example_instruction_output =example_prompt_response,
        )

        whole_prompt = f"{system_message}\n\n{user_prompt}"

        print("##############################Whole Prompt:####################################" )
        print(f"Question : {index+1}")
        print(f"{whole_prompt}")

        # print(f"{whole_prompt}\n\n")
        # llm_response = quick_ask(
        #     prompt=whole_prompt, token_counter=None, model_name="gpt-4o"
        # )

        llm_response = quick_ask(
        prompt = whole_prompt,
        token_counter=None,  # Replace with actual token counter if available
        model_name="gpt-4o-2024-05-13",
        max_tokens=1000,
        verbose=True,
        json_output=True,
        temperature=0.0
    )
        # save gpt_outputs
        print("########################### successfully created gpt output for question ", index)
        print(f"############################ The LLM response is: {llm_response}")  # Print the Llm_response)

        ############ Code for saving the responses ############
        llm_response_cleaned = llm_response.strip()

        # Optional: Step 2 - If you know the exact pattern of the indentation or unwanted characters, remove them
        # For example, if there are known leading spaces on each line, you might do something like this:
        llm_response_cleaned = "\n".join(line.lstrip() for line in llm_response_cleaned.splitlines())

        # Step 3: Attempt to convert the cleaned string to a dictionary
        try:
            converted_dict = ast.literal_eval(llm_response_cleaned)
            # Ensure the dictionary was successfully created before modifying it
            if isinstance(converted_dict, dict):
                converted_dict["Expected_output"] = sample_instructions[index]["output"]
                print(converted_dict)  # Optional: for verification
            else:
                print("Parsed data is not a dictionary.")
        except (ValueError, SyntaxError) as e:
            print(f"Error converting string to dict: {e}")
            try:
                converted_dict = json.loads(llm_response_cleaned)
            except json.JSONDecodeError as e:
                print(f"Error converting string to JSON: {e}")
                converted_dict = {"response": llm_response_cleaned }
        except IndexError:
            print("Index out of range when accessing sample_instructions.")
        # Collect each question and its corresponding answer in the dictionary
        qa_pairs.append(
            converted_dict  
        )

    # Specify the JSON output file path
    json_file_path = "output/gpt/alpaca_eval_1.json"

    # Save the collected question-answer pairs to a JSON file
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=4)

    print("All responses have been saved to JSON.")
        
    
    ############ Code for scoring the responses ############ 
        ######## This code should be inside the for loop as well 
        
    # system_message, user_prompt = score_llm_prompt(
    #     prompt=current_prompt, llm_output=llm_response, rubric=example_rubric
    # )

    # whole_prompt = f"{system_message}\n\n{user_prompt}"

    # print("Whole Prompt:")
    # print(f"{whole_prompt}")

    # # print(f"{whole_prompt}\n\n")
    # llm_response = quick_ask(prompt=whole_prompt, token_counter=None)

    # # Specify the directory and filename
    # file_path = f"output/gpt/{key}_final_essay_gpt_scored.docx"

    # # Create a new Document
    # doc = Document()
    # doc.add_paragraph(llm_response)  # Adding the text as a new paragraph

    # # Save the document to the specified file path
    # doc.save(file_path)


run_gpt()


