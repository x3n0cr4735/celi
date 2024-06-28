import json
import os
import math

def split_instructions(input_file, output_folder, questions_per_file=10):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Calculate the number of files needed
    num_files = math.ceil(len(data) / questions_per_file)

    for i in range(num_files):
        # Get the slice of data for this file
        start = i * questions_per_file
        end = min((i + 1) * questions_per_file, len(data))
        file_data = data[start:end]

        # Create the output filename
        output_file = os.path.join(output_folder, f'instructions_set_{i+1}.json')

        # Write the data to the output file
        with open(output_file, 'w') as f:
            json.dump(file_data, f, indent=2)

        print(f"Created file: {output_file} with {len(file_data)} questions")

# Usage
input_file = 'data/working_data/instructions/instructions_all.json'  # Replace with your input file path
output_folder = 'data/working_data/instructions/instruction_set'
questions_per_file = 10

split_instructions(input_file, output_folder, questions_per_file)