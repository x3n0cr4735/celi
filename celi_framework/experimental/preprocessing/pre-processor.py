"""
celi_framework.pre-processor
This script outlines a comprehensive workflow for processing DOCX documents into a cleaned format that is primed for the embedding process in the celi_framework.embeddor module. It employs a variety of utilities to convert, extract, cleanse, and standardize document content, preparing it for advanced machine learning tasks. The process includes:

1. Converting DOCX documents to Markdown format using Pandoc, making subsequent text manipulation tasks more straightforward.
2. Employing custom functions to parse the converted Markdown, extracting specific sections according to a predefined schema.
3. Implementing cleaning and standardization techniques to refine the text, including the removal of superfluous headings and newline characters.
4. Saving the processed content in JSON format, which is structured and ready for the embedding processes executed by the celi_framework.embeddor module.

Key components include:
- `convert_docx_to_markdown`: Converts DOCX files to Markdown for improved text accessibility.
- `process_markdown_fill_flat_2`, `process_markdown_fill_flat_3`, `process_markdown_fill_flat_4`: Varied strategies for section content extraction from Markdown, tailored for different document structures.
- `heading_standardization`: Streamlines section headings for consistent extraction and subsequent embedding.
- `test_load_json_files`: Confirms JSON file integrity, crucial for successful loading and embedding.
- `rid_new_line_sections_dict`: Purges sections of unnecessary newlines, reducing noise before embedding.
- `process_files_in_directory_new_line`: Implements newline cleanup across multiple files in preparation for embedding.
- `clean_up_dict`: Applies an in-depth content cleanup, utilizing AI models to polish text for optimal embedding results.
- `process_files_in_directory`: Coordinates the document processing workflow, ensuring each file is systematically cleaned and ready for the celi_framework.embeddor module.

This script is built to be adaptable, enabling users to tailor its functions to meet the unique requirements of their projects. It serves as an exemplar for document preprocessing, showcasing Python's capabilities for automating the preparation of textual data for intricate analysis and model training.

"""

# TODO -> We manually had chatGPT take table of contents and turn it into a dictionary "schema" for our experimentation.
#  Do this programatically at some point


import json
import os
import re
import subprocess
import time

from celi_framework.experimental.templates import make_cleanup_dict_prompt_template
from celi_framework.utils.llms import quick_ask
from celi_framework.utils.log import (
    app_logger as logger,
)  # TODO: Check that the logger works correctly
from celi_framework.utils.token_counters import token_counter_og
from celi_framework.utils.utils import (
    load_json,
    save_json,
    filter_empty_sections,
    read_txt,
)


# STEP 1
def convert_docx_to_markdown(input_file, output_file):
    """
    Converts a DOCX file to Markdown format using Pandoc.

    Args:
    input_file (str): Path to the input DOCX file.
    output_file (str): Path for the output Markdown file.
    """
    try:
        # Constructing the command
        command = [
            "pandoc",
            "-f",
            "docx",
            "-t",
            "markdown",
            input_file,
            "-o",
            output_file,
        ]

        # Executing the command
        subprocess.run(command, check=True)
        print(f"Conversion successful: {input_file} to {output_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred during conversion: {e}")


def process_markdown_fill_flat_2(file_path, section_dict):
    """
    Process a markdown file and store sections in a dictionary based on a provided section dictionary.
    This version uses regular expressions to match markdown headings and considers their levels.

    Args:
    file_path (str): Path to the markdown file.
    section_dict (dict): Dictionary with section numbers as keys and section titles as values.

    Returns:
    dict: A dictionary where keys are section numbers and values are the content of each section.
    """
    sections = {
        key: "" for key in section_dict.keys()
    }  # Initialize dictionary for content
    current_section = None
    section_pattern = re.compile(r"(#+)\s+(.*)")  # Pattern to match markdown headings

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = section_pattern.match(line)
            if match:
                heading_level = len(
                    match.group(1)
                )  # Number of '#' symbols indicates the level
                section_title = match.group(2).strip()
                for sec_number, sec_title in section_dict.items():
                    if (
                        sec_title.upper() == section_title.upper()
                    ):  # Case-insensitive comparison
                        # Only update current_section if the heading level matches the section number format
                        if sec_number.count(".") + 1 == heading_level:
                            current_section = sec_number
                            break
                else:
                    current_section = None  # No matching section found

            if (
                current_section and not match
            ):  # Accumulate content if we are in a section and it's not a heading
                sections[current_section] += line

    return sections


def process_markdown_fill_flat_3(text, section_dict):
    """
    Process a markdown-like text and store sections in a dictionary based on a provided section dictionary.
    Args:
    text (str): Text to be processed.
    section_dict (dict): Dictionary with section numbers as keys and section titles as values.
    Returns:
    dict: A dictionary where keys are section numbers and values are the content of each section.
    """
    sections = {
        key: "" for key in section_dict.keys()
    }  # Initialize dictionary for content
    current_section = None
    lines = text.split("\n")

    for line in lines:
        print(f"Processing line: {line}")  # Debugging statement
        # Check if line is a section title
        for sec_number, sec_title in section_dict.items():
            if line.strip().startswith(
                f"**{sec_title}**"
            ):  # Adjusted check for bold headers
                current_section = sec_number
                sections[current_section] = line + "\n"  # Add the title line
                print(f"Found section: {sec_title}")  # Debugging statement
                break
        else:
            # If not a section title, add line to the current section's content
            if current_section:
                sections[current_section] += line + "\n"

    return sections


def process_markdown_fill_flat_4(text, section_dict, debug=False):
    """
    Process a markdown-like text and store sections in a dictionary based on a provided section dictionary.

    Args:
        text (str): Text to be processed.
        section_dict (dict): Dictionary with section numbers as keys and section titles as values.
        debug (bool): Flag to control debugging print statements.

    Returns:
        dict: A dictionary where keys are section numbers and values are the content of each section.
    """
    sections = {
        key: "" for key in section_dict.keys()
    }  # Initialize dictionary for content
    current_section = None
    lines = text.split("\n")

    for line in lines:
        if debug:
            print(f"Processing line: {line}")  # Debugging statement

        is_section_title = False

        # Flexible section identification
        for sec_number, sec_title in section_dict.items():
            # Regex for different header levels and bold text
            header_pattern = rf"^(#+ |\*\*){re.escape(sec_title)}(\*\*)?$"
            if re.match(header_pattern, line.strip()):
                # Additional check to confirm it's a section header
                if line.strip().startswith("#") or line.strip().startswith("**"):
                    current_section = sec_number
                    is_section_title = True
                    if debug:
                        print(f"Found section: {sec_title}")  # Debugging statement
                    break

        # Append the line to the current section, skip section headers
        if current_section and not is_section_title:
            sections[current_section] += line + "\n"

    return sections


def heading_standardization(input_dict):
    """
    Assumes a flat filled dict, already cleaned for embeddings.
    This function checks if each non-empty section in the input dictionary starts with a heading.
    The function checks if the first part of the content before '\n\n' is short enough to be a heading.
    If no headings are present, or if the first part is too long, it returns the input dictionary with no changes.
    If a valid heading is present, it separates the heading out and returns a dictionary with headings removed.

    Parameters:
    input_dict (dict): Dictionary with sections and content where headings might be present.

    Returns:
    dict: Dictionary with headings removed from the content.
    """
    heading_removed_dict = {}
    heading_present = False
    max_heading_length = 100  # Maximum length of what we consider a heading

    for key, value in input_dict.items():
        if value:  # Check if the section is not empty
            split_content = value.split(
                "\n\n", 1
            )  # Splitting at the first occurrence of '\n\n'
            if len(split_content) > 1 and len(split_content[0]) <= max_heading_length:
                # Heading is present and its length is within the limit
                heading_removed_dict[key] = split_content[
                    1
                ]  # Content without the heading
                heading_present = True
            else:
                # No heading detected (or not in the expected format, or too long)
                heading_removed_dict[key] = value
        else:
            # Empty section, just copy it
            heading_removed_dict[key] = value

    if not heading_present:
        print("No headings present or headings too long, no changes needed.")
        return input_dict

    return heading_removed_dict


def test_load_json_files(directory):
    """
    Check each file in the specified directory to see if it's a valid JSON file.

    Args:
    directory (str): The path to the directory containing the JSON files.

    Returns:
    dict: A dictionary with filenames as keys and a boolean indicating successful loading as values.
    """
    results = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, "r") as file:
                    json.load(file)
                results[filename] = True
            except json.JSONDecodeError:
                results[filename] = False
    return results


def rid_new_line_sections_dict(input_dict):
    """
    Processes a dictionary to remove entries where the value consists solely of newline characters.

    This function iterates through each key-value pair in the input dictionary. If a value is found
    to consist only of newline characters ('\n'), it replaces that value with an empty string.
    Otherwise, the original value is retained. The function returns a new dictionary with these processed values.

    Args:
    input_dict (dict): A dictionary with string values to be processed.

    Returns:
    dict: A new dictionary where values consisting only of newline characters are replaced with empty strings.
    """
    processed_dict = {}
    for key, value in input_dict.items():
        if all(char == "\n" for char in value):
            processed_dict[key] = ""
        else:
            processed_dict[key] = value
    return processed_dict


def process_files_in_directory_new_line(directory, filename_pattern):
    """
    Process all files in the given directory that match the filename pattern.

    Args:
    directory (str): Path to the directory.
    filename_pattern (str): Pattern to match in filenames.

    """
    for filename in os.listdir(directory):
        if filename_pattern in filename:
            file_path = os.path.join(directory, filename)

            # Read the file
            with open(file_path, "r") as file:
                try:
                    content = json.load(file)
                except json.JSONDecodeError:
                    logger.error(f"Error reading JSON from {file_path}. Skipping file.")
                    continue

            # Process the dictionary
            processed_content = rid_new_line_sections_dict(content)

            # Write the processed content back to the file
            with open(file_path, "w") as file:
                json.dump(processed_content, file, indent=4)
                print(f"Processed and saved {file_path}")


def clean_up_dict(input_dict, schema_dict, section_numbers_to_process=None):
    """
    Cleans up the content of the given dictionary by processing its text through an AI model. It also
    identifies and stores details of problem sections and manages token usage.
    Optionally processes only specified sections.

    Args:
        input_dict (dict): Dictionary containing the content to be cleaned. It can be flat or nested.
        schema_dict (dict): Dictionary containing the schema for the sections.
        section_numbers_to_process (list, optional): List of section numbers to be processed.

    Returns:
        tuple(dict, dict): A tuple containing the cleaned dictionary and a dictionary of problem sections.
    """
    # Dictionary to track sections with problems
    problem_sections = {}
    # Counter for the total number of tokens used in queries
    total_tokens_used = 0
    # Set a limit for the number of tokens that can be used per minute
    TOKEN_LIMIT_PER_MINUTE = 150000

    # Iterate through each section in the input dictionary
    for section_number, content in input_dict.items():
        # Retrieve the heading for the current section from the schema
        section_heading = schema_dict[section_number]

        # Skip sections not in the provided list, if such a list is specified
        if (
            section_numbers_to_process is not None
            and section_number not in section_numbers_to_process
        ):
            continue

        # Log the start of processing for this section
        print(f"Starting {section_number}")

        # Handle both nested and flat dictionary structures
        if isinstance(content, dict):
            # Extract the content if it's nested under a 'content' key
            section_content = content.get("content", "")
        else:
            # Directly use the content if the dictionary is flat
            section_content = content

        # Process the content if it is not just whitespace
        if section_content and len(section_content.strip("")) > 0:
            # Generate a cleanup prompt for the AI model
            prompt = make_cleanup_dict_prompt_template(
                section_content, section_heading, schema_dict
            )
            # Log the generated prompt
            print("Prompt")
            print(prompt)

            # Count the tokens in the prompt to manage usage
            tokens = token_counter_og(prompt)
            total_tokens_used += tokens

            # If the token limit is reached, pause to reset the token count
            if total_tokens_used >= TOKEN_LIMIT_PER_MINUTE:
                print("Token limit reached, sleeping for 60 seconds...")
                time.sleep(2)  # Sleep for 60 seconds
                total_tokens_used = tokens  # Reset the token count

            try:
                # Send the prompt to the AI model and get a response
                response_str = quick_ask(
                    prompt,
                    json_output=True,
                    max_retries=2,
                    timeout=None,
                    model_name="gpt-4-0125-preview",
                )
            except:
                # Handle exceptions in getting a response
                problem_sections[section_number] = {
                    "content": "",
                    "reason": "Failed to get response from OpenAI",
                }
                input_dict[section_number] = ""
                continue

            try:
                # Try to parse the AI model's response as JSON
                response = (
                    json.loads(response_str)
                    if isinstance(response_str, str)
                    else response_str
                )
            except json.JSONDecodeError:
                # Handle JSON parsing errors
                logger.error(
                    f"Error parsing response for section {section_number}. Response: {response_str}"
                )
                continue

            # Check the response for actions to take
            if "action" in response and response["action"] == "save":
                # Save the cleaned text in the input dictionary
                if isinstance(content, dict):
                    input_dict[section_number]["content"] = response["cleaned_text"]
                else:
                    input_dict[section_number] = response["cleaned_text"]
            elif "action" in response and response["action"] == "skip":
                # Skip the section and record the reason
                problem_sections[section_number] = {
                    "content": content,
                    "reason": response["reason"],
                }
                if isinstance(content, dict):
                    input_dict[section_number]["content"] = ""
                else:
                    input_dict[section_number] = ""
            else:
                # Handle unexpected response formats
                print(
                    f"Unexpected response format for section {section_number}. Response: {response}"
                )

        # Indicate completion of processing for this section
        print(f"Finished with {section_number}")

    # Return the cleaned input dictionary and the dictionary of problem sections
    return input_dict, problem_sections


def process_files_in_directory(
    directory, filename_pattern_filled, filename_pattern_schema
):
    """
    Process all files in the given directory that match the filename patterns.

    Args:
    directory (str): Path to the directory.
    filename_pattern_filled (str): Pattern to match in filled filenames.
    filename_pattern_schema (str): Pattern to match in schema filenames.

    # Example usage
    directory_path = [PUT HERE]
    filename_pattern_filled = '_flat_filled.json'
    filename_pattern_schema = '_flat_schema.json'
    process_files_in_directory(directory_path, filename_pattern_filled, filename_pattern_schema)
    """
    filled_files = [f for f in os.listdir(directory) if filename_pattern_filled in f]

    # TODO -> Remove these!!!!!
    filled_files = [f for f in filled_files if "Name" not in f]  # TODO -> Replace Name
    filled_files = [f for f in filled_files if "Name" not in f]  # TODO ->  Replace Name

    for filled_file in filled_files:
        prefix = filled_file.split("_flat_filled")[0]
        schema_file = prefix + filename_pattern_schema

        if schema_file in os.listdir(directory):
            filled_file_path = os.path.join(directory, filled_file)
            schema_file_path = os.path.join(directory, schema_file)

            # Load the content of the files
            dict_to_be_cleaned = load_json(filled_file_path)
            dict_schema = load_json(schema_file_path)

            # Process the dictionary
            cleaned_dict, problems = clean_up_dict(dict_to_be_cleaned, dict_schema)

            # Save the cleaned dictionary and problems
            cleaned_file_path = filled_file_path.replace(
                ".json", "_cleaned_for_embed.json"
            )
            problems_file_path = filled_file_path.replace(
                ".json", "_cleaned_problems.json"
            )

            save_json(cleaned_dict, cleaned_file_path)
            save_json(problems, problems_file_path)
            print(f"Processed and saved {cleaned_file_path} and {problems_file_path}")


def process_doc_to_completion(file_paths):
    """
    This function orchestrates the conversion of a DOCX file to a cleaned and processed Markdown file suitable
    for embedding in a machine learning model. It involves several steps including conversion from DOCX to Markdown,
    section extraction, cleanup, and formatting.

    The process includes:
    1. Converting a DOCX file to Markdown format.
    2. Loading a predefined schema for section extraction.
    3. Extracting and standardizing sections from the Markdown file.
    4. Cleaning up the extracted sections for embedding.
    5. Saving the cleaned data and any identified problems.
    6. Creating and saving a filtered schema based on the cleaned data.

    Args:
        file_paths (dict): A dictionary containing all necessary file paths. Keys include:
            'json_saves_path', 'docx_filepath', 'md_filepath', 'schema_filepath',
            'flat_filled_filepath', 'flat_filled_cleaned_filepath', 'flat_filled_clean_problems_filepath',
            'schema_for_mapping_filepath'.
    """

    # Step 1: Convert DOCX to Markdown
    # Utilizes Pandoc to convert the document format
    convert_docx_to_markdown(file_paths["docx_filepath"], file_paths["md_filepath"])

    # Step 2: Load the predefined schema for section extraction
    schema = load_json(file_paths["schema_filepath"])

    # Step 3: Extract and standardize sections from the Markdown
    flat_filled = process_markdown_fill_flat_4(
        text=read_txt(file_paths["md_filepath"]), section_dict=schema
    )
    flat_filled = heading_standardization(flat_filled)  # Removes headings from sections

    # Step 4: Cleanup sections for embedding
    flat_filled = rid_new_line_sections_dict(
        flat_filled
    )  # Cleans up sections with only new lines
    save_json(
        flat_filled, file_paths["flat_filled_filepath"]
    )  # Saves the intermediate result

    cleaned_dict, problems = clean_up_dict(flat_filled, schema)
    save_json(
        cleaned_dict, file_paths["flat_filled_cleaned_filepath"]
    )  # Saves the cleaned data
    save_json(
        problems, file_paths["flat_filled_clean_problems_filepath"]
    )  # Saves any problems identified

    # Step 5: Create and save a filtered schema
    filtered_protocol_schema = filter_empty_sections(
        toc_dict=schema, content_dict=flat_filled
    )
    save_json(filtered_protocol_schema, file_paths["schema_for_mapping_filepath"])


if __name__ == "__main__":
    file_paths = {
        "json_saves_path": "./processed_docs/json/",
        "docx_filepath": "./docs/raw/sample.docx",
        "md_filepath": "./docs/markdown/sample.md",
        "schema_filepath": "./schemas/sections_schema.json",
        "flat_filled_filepath": "./processed_docs/json/sample_flat_filled.json",
        "flat_filled_cleaned_filepath": "./processed_docs/json/sample_flat_filled_cleaned.json",
        "flat_filled_clean_problems_filepath": "./processed_docs/json/sample_flat_filled_clean_problems.json",
        "schema_for_mapping_filepath": "./processed_docs/json/sample_schema_for_mapping.json",
    }

    process_doc_to_completion(file_paths)
