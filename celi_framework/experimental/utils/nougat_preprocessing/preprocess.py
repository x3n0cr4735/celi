import re

from celi_framework.utils.llms import quick_ask
from celi_framework.experimental.utils.nougat_preprocessing.preprocessing_templates import (
    make_correct_mmd_output,
    make_parse_clean_tables_2,
    make_remove_table_syntax,
)


# TODO - run this on an EC2
# !nougat documents_for_src/document_dump/synthetic/[DOCUMENT NAME].pdf --out documents_for_src/md/nougat --no-skipping -m 0.1.0-base
# !nougat pdf documents_for_src/document_dump/synthetic/[DOCUMENT NAME].pdf --out documents_for_src/md/nougat --no-skipping -m 0.1.0-base


def read_mmd(file_path):
    """
    Reads the content of a file from a given path with UTF-8 encoding, falling back to Latin-1 on UnicodeDecodeError.

    Args:
        file_path (str): The path of the file to be read.

    Returns:
        str: The content of the file as a string.
    """
    # Try reading the file using UTF-8 encoding
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    # If UnicodeDecodeError occurs, try reading with Latin-1 encoding
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as file:
            return file.read()


def fix_mmd(doc_text, section=None, whole_document=False):
    """
    Processes a document or a specific section to correct formatting issues.

    Args:
        doc_text (str): The text of the document.
        section (str, optional): The specific section number to be processed. Defaults to None.
        whole_document (bool, optional): If True, processes the entire document. Defaults to False.

    Returns:
        str or None: The processed text of the specified section or entire document, or None if section not found.
    """
    # Decide whether to process the whole document or just a specified section
    if whole_document:
        section_content = doc_text
    elif section:
        # Create a regex pattern to find the specified section
        pattern = r"(?<=## {}\s)(.*?)(?=## \d)".format(section)
        # Use regex to search for the section in the document
        match = re.search(pattern, doc_text, re.DOTALL)
        # If the section is found, extract its content
        if match:
            section_content = match.group(0).strip()
        else:
            # If the section is not found, return None and print a message
            print(f"Section {section} not found.")
            return None
    else:
        # If neither whole document nor a section is specified, print a message and return None
        print("Please provide a section or set whole_document to True.")
        return None

    # Format the content for processing
    formatted_prompt = make_correct_mmd_output(section_content)
    # Get the processed response from the external processing function (e.g., GPT model)
    response = quick_ask(
        formatted_prompt, max_tokens=4000, model_name="gpt-4-0613", json_mode=False
    )
    # Return the processed response
    return response


def split(doc_text, print_output=False):
    """
    Splits the document into sections based on markdown-style headers.

    Args:
        doc_text (str): The text of the document.
        print_output (bool, optional): If True, prints the content of each section. Defaults to False.

    Returns:
        dict: A dictionary with section numbers as keys and details (title and text) as values.
    """
    # Regex pattern to identify markdown headers with section numbers
    section_pattern = re.compile(r"^#+( \d+(\.\d+)*) (.+)$", re.MULTILINE)
    # Initialize a dictionary to store sections
    sections = {}
    # Variable to track the last identified section number
    last_section_num = None

    # Iterate through each line in the document
    for line in doc_text.split("\n"):
        # Try to match the line with the section pattern
        match = re.match(section_pattern, line)
        if match:
            # Extract the section number and title
            section_num = match.group(1)
            section_title = match.group(3)
            # Initialize the section in the dictionary
            sections[section_num.strip()] = {"title": section_title, "text": ""}
            # Update the last section number for subsequent text appending
            last_section_num = section_num.strip()
        elif last_section_num is not None:
            # Append the line to the text of the current section
            sections[last_section_num]["text"] += line + "\n"

    # Remove extra whitespace at the end of each section
    for sec_num, content in sections.items():
        sections[sec_num]["text"] = sections[sec_num]["text"].rstrip()

        # Optionally print each section's details
        if print_output:
            print(
                f"Section {sec_num} {content['title']}: {content['text']}\n{'='*50}\n"
            )

    # Return the dictionary containing all sections
    return sections


def split2(doc_text, print_output=False):
    """
    Alternative implementation of split function, handling both markdown and non-markdown styled headers.

    Args:
        doc_text (str): The text of the document.
        print_output (bool, optional): Flag to print each section's output. Defaults to False.

    Returns:
        dict: A dictionary of sections with numbers, titles, and text.
    """
    # Regex pattern to identify section headings with or without markdown '#' prefix
    section_pattern = re.compile(r"^(#+ )?(\d+(\.\d+)*)( .+)?$", re.MULTILINE)
    # Initialize a dictionary to hold sections
    sections = {}
    # Track the last section number identified
    last_section_num = None

    # Process each line in the document
    for line in doc_text.split("\n"):
        # Match the line with the section heading pattern
        match = re.match(section_pattern, line)
        if match:
            # Extract the section number and title, handling cases with missing titles
            section_num = match.group(2)
            section_title = match.group(4) if match.group(4) else ""
            # Add the section to the dictionary with trimmed details
            sections[section_num.strip()] = {"title": section_title.strip(), "text": ""}
            # Update the last section number
            last_section_num = section_num.strip()
        elif last_section_num is not None:
            # Append the line to the text of the last identified section
            sections[last_section_num]["text"] += line + "\n"

    # Post-processing to remove trailing whitespace
    for sec_num, content in sections.items():
        sections[sec_num]["text"] = sections[sec_num]["text"].rstrip()

        # Optionally print the section details
        if print_output:
            print(
                f"Section {sec_num} {content['title']}: {content['text']}\n{'='*50}\n"
            )

    # Return the sections dictionary
    return sections


def identify_sections_with_tables(dict_report):
    """
    Identifies sections of a document that contain tables.

    Args:
        dict_report (dict): A dictionary representation of the document sections.

    Returns:
        list: A list of section numbers that contain tables.
    """
    # Initialize a list to store sections that contain tables
    sections_with_tables = []
    # Iterate through each section in the document
    for section, content in dict_report.items():
        # Check if the section contains LaTeX table syntax
        # Looks for either 'tabular' or 'table' keywords in the section text
        if "{tabular}" in content["text"] or "{table}" in content["text"]:
            # If found, add the section number to the list
            sections_with_tables.append(section)

    # Return the list of sections with tables
    return sections_with_tables


def parse_tables_from_sections(section, dict_report):
    """
    Parses tables from a specified section of the document.

    Args:
        section (str): The section number.
        dict_report (dict): The dictionary containing the document sections.

    Returns:
        str: The processed response after parsing tables from the section.
    """
    # Extract the text of the specified section
    section_content = dict_report[section]["text"]
    # Format the section content for parsing tables
    formatted_prompt = make_parse_clean_tables_2(section, section_content)
    # Use an external function (e.g., a GPT model) to parse the tables
    response = quick_ask(
        formatted_prompt,
        max_tokens=4000,
        model_name="gpt-4-1106-preview",
        json_mode=False,
    )
    # Return the processed response from the parsing operation
    return response


def remove_table_syntax(section_content):
    """
    Removes table syntax from a given section content.

    Args:
        section_content (str): The content of a document section.

    Returns:
        str: Processed content with table syntax removed.
    """
    # Format the section content for removing table syntax
    formatted_prompt = make_remove_table_syntax(section_content)
    # Use an external function to process and remove the table syntax
    response = quick_ask(
        formatted_prompt, max_tokens=4000, model_name="gpt-4-0613", json_mode=False
    )
    # Return the processed content with the table syntax removed
    return response


# Continue adding comments for the remaining functions in a similar manner.


def parse_table_content(table_dict, section, model_name="gpt-4-0613"):
    """
    Parses and structures the content of LaTeX tables in a given section using a specified model.

    Args:
        table_dict (dict): Dictionary containing table headings and contents.
        section (str): The section number.
        model_name (str, optional): The model name used for parsing. Defaults to "gpt-3".

    Returns:
        dict: A dictionary with parsed and structured table data.
    """
    # Initialize a dictionary to hold the parsed table data
    parsed_table = {}
    # Iterate over each table heading and content in the given dictionary
    for table_heading, table_content in table_dict.items():
        # Format the prompt with section details and table content for parsing
        formatted_prompt = f"I have a slightly ill-structured LaTeX table under section {section} with the title '{table_heading}'. The content of the table is: {table_content}. Could you help me clean it up and present it in a well-structured format?"
        # Use an external function (e.g., a GPT model) to parse and structure the table content
        response = quick_ask(formatted_prompt, model_name)
        # Store the parsed table content in the dictionary
        parsed_table[table_heading] = response

    # Return the dictionary containing the parsed and structured tables
    return parsed_table


def clean_section_tables(dict_report, section):
    """
    Cleans up tables in a given section of the document.

    Args:
        dict_report (dict): The dictionary representation of the document sections.
        section (str): The section number.

    Returns:
        dict: A dictionary of cleaned tables within the section.
    """
    # Extract the text content of the specified section
    section_content = dict_report[section]["text"]
    # Split the section content into lines for processing
    lines = section_content.split("\n")
    # Initialize a dictionary to hold cleaned tables
    cleaned_tables = {}
    # Variables to keep track of the current table's content and heading
    current_table_content = ""
    current_table_heading = ""

    # Iterate through each line in the section
    for line in lines:
        # Check if the line marks the beginning of a table
        if line.strip() == "\\begin{tabular}":
            # Start capturing the table content
            current_table_content = line + "\n"
        # Check if the line marks the end of a table
        elif line.strip() == "\\end{tabular}":
            # Finish capturing the table content
            current_table_content += line + "\n"
            # Parse and clean the current table content
            cleaned_tables[current_table_heading] = parse_table_content(
                {current_table_heading: current_table_content}, section
            )
            # Reset the table content and heading for the next table
            current_table_content = ""
            current_table_heading = ""
        # If currently capturing a table, continue appending lines to its content
        elif current_table_content:
            current_table_content += line + "\n"
        # Otherwise, treat the line as a potential table heading
        else:
            if line.strip() and (not line.strip().startswith("#")):
                current_table_heading = line.strip()

    # Return the dictionary of cleaned tables
    return cleaned_tables


def generate_section_tables_report(dict_report, section):
    """
    Generates a report of tables in a given section after cleaning and parsing.

    Args:
        dict_report (dict): The dictionary representation of the document sections.
        section (str): The section number.

    Returns:
        str: A report of the tables in the specified section.
    """
    # Clean and parse the tables in the specified section
    cleaned_tables = clean_section_tables(dict_report, section)
    # Initialize a string to hold the report
    report = f"Section {section}:\n"
    # Append each table heading and its cleaned content to the report
    for table_heading, table_content in cleaned_tables.items():
        report += f"\n{table_heading}:\n{table_content}\n"

    # Return the final report string
    return report
