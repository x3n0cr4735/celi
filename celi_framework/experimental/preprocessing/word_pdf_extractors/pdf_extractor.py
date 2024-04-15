"""
This script is designed to extract text and tables from PDF documents and process the extracted content into structured formats. It leverages the PyMuPDF library (fitz module) for interacting with PDFs, regex for text processing, and pandas for formatting table data into Markdown. The script supports extracting content from specific sections defined by the document's table of contents (ToC), identifying text between sections, and replacing references to tables within the text with their Markdown representations.

Key functionalities include:
- Extracting text and tables from specified page ranges within a PDF document.
- Determining and extracting text that resides between specified section headings.
- Replacing table references in the text with Markdown-formatted tables.
- Orchestrating the extraction process across a PDF document's sections, based on its ToC, and saving the structured output in JSON format.

Dependencies:
- os: For interacting with the file system.
- fitz (PyMuPDF): For reading PDF documents and extracting content.
- regex: For advanced regular expression matching and text processing.
- pandas: For data manipulation and converting table data into Markdown format.

The script utilizes helper functions from an external module 'extractor_helpers' for navigation between sections and saving the extracted data. It sets pandas display options to ensure that table data is formatted correctly when converted to Markdown. The script is structured to be modular, making it adaptable for various extraction and processing needs involving PDF documents.

Usage:
This script can be used as part of a larger data extraction pipeline, content management system, or any application requiring structured extraction and processing of PDF document content.

Note: Docstrings and comments were made by Sam.
"""

import os
import json
import fitz
import regex
import pandas as pd

from .extractor_helpers import save_to_json, toc_iterator
from celi_framework.core.templates import make_toc_prompt
from celi_framework.utils.llms import quick_ask
from celi_framework.utils.token_counters import get_master_counter_instance

pd.set_option("display.max_colwidth", 0)


def create_toc(doc):
    """
    Generates a structured table of contents (ToC) for a PDF document using LLM.
    """
    all_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        all_text += f"\nPage {page_num + 1}:\n{text}"

    prompt = make_toc_prompt(all_text)
    response = quick_ask(
        prompt, json_output=True, token_counter=get_master_counter_instance()
    )
    toc_dict = json.loads(response)
    toc = convert_dict_to_toc(toc_dict)
    return toc


def convert_dict_to_toc(toc_dict):
    """
    Converts a dictionary containing a ToC to a list of lists format.
    """
    return [
        [entry["section_number"], entry["section_name"], entry["page_number"]]
        for entry in toc_dict["toc"]
    ]


def get_between_section_text_and_tables(start_page, end_page, target_doc):
    """
    Extracts all text and tables between specified start and end pages in a PDF document.

    Parameters:
    - start_page (int): The starting page number (1-indexed) from which to begin extraction.
    - end_page (int): The ending page number (1-indexed) up to which extraction should continue.
    - target_doc (Document): The PDF document object from which to extract text and tables.

    Returns:
    - tuple: A tuple containing the concatenated text (`full_text`) from all pages within the range
             and a list of tables (`tables`). Each table is represented as a tuple of its header names
             and extracted content.

    Details:
    Iterates through each page in the specified range, appending the page's text to `full_text`
    and accumulating tables found on the page.
    """

    full_text = ""
    tables = []
    for page_num in range(start_page - 1, end_page):
        t_page = target_doc[page_num]
        full_text += t_page.get_text()
        tables.extend([(t.header.names, t.extract()) for t in t_page.find_tables()])
    return full_text, tables


def determine_inbetween_text(curr_section_name, next_section_name, full_text):
    """
    Identifies and extracts the text that occurs between the headings of the current and next sections within a larger text body.

    Parameters:
    - curr_section_name (str): The name (heading) of the current section.
    - next_section_name (str): The name (heading) of the following section.
    - full_text (str): The full text in which to search for the section names.

    Returns:
    - str: A string containing the text found between the two section names. If the next section name is
           not provided, it returns the text following the current section name.

    Details:
    Uses a regular expression to locate the section of text between the provided headings, handling
    optional presence of the next section name.
    """

    print(f"Current section name: {curr_section_name}")
    print(f"Next section name: {next_section_name}")
    print(f"Full text length: {len(full_text)}")

    pattern = rf"(?:{curr_section_name})(.*)"

    if next_section_name:
        pattern += rf"(?:{next_section_name})"

    print(f"Regular expression pattern: {pattern}")

    matches = regex.search(pattern, full_text.replace("\n", ""), regex.IGNORECASE)

    if matches:
        print("Match found!")
        extracted_text = matches.group(1).strip()
        print(f"Extracted text length: {len(extracted_text)}")
        return extracted_text
    else:
        print("No match found.")
        return ""


def replace_tables_in_section(inbetween_text, target_table_tuple):
    """
    Searches for a specific table within a text section and replaces its reference with a Markdown-formatted table.

    Parameters:
    - inbetween_text (str): The text of a document section potentially containing table references.
    - target_table_tuple (tuple): A tuple containing the table's header names and its extracted content.

    Returns:
    - str: The input text with the specified table replaced by a Markdown representation of the table.

    Details:
    Constructs a regular expression to find the table within the text and replaces it with its Markdown
    equivalent, using `pandas` for Markdown conversion.
    """

    table_header, table_extract = target_table_tuple
    table_header = [
        str(element) if element is not None else "" for element in table_header
    ]

    # Remove empty rows from the table_extract
    table_extract = [
        row for row in table_extract if any(cell is not None for cell in row)
    ]

    # Check if the table has at least one row
    if len(table_extract) > 0:
        last_cell_text = " ".join(
            [str(i) if i is not None else "" for i in table_extract[-1]]
        ).replace("\n", " ")

        # Try to find the table using the new format (without considering header text)
        pat_new = rf"(?:{regex.escape(last_cell_text, literal_spaces=True)}){{e<=1}}"
        mat_new = regex.search(pat_new, inbetween_text)

        if mat_new:
            md_table = pd.DataFrame(table_extract, columns=table_header).to_markdown()
            inb_text_w_replaced_section = regex.sub(
                pat_new, str(md_table), inbetween_text
            )
            return inb_text_w_replaced_section
        else:
            # Try to find the table using the previous format (considering header text)
            pat_old = rf"(?:{regex.escape(' '.join(table_header), literal_spaces=True)}){{e<=1}}.*(?:{regex.escape(last_cell_text, literal_spaces=True)}){{e<=1}}"
            mat_old = regex.search(pat_old, inbetween_text)

            if mat_old:
                md_table = pd.DataFrame(
                    table_extract, columns=table_header
                ).to_markdown()
                inb_text_w_replaced_section = regex.sub(
                    pat_old, str(md_table), inbetween_text
                )
                return inb_text_w_replaced_section

    return inbetween_text


def extract_from_pdf(doc_filepath, output_folder):
    """
    Orchestrates the extraction of text and tables from a PDF document, processing each section defined in
    the document's table of contents (ToC).

    Parameters:
    - doc_filepath (str): Path to the PDF file from which to extract data.
    - output_folder (str): Directory where the extracted data will be saved as JSON files.

    Returns:
    - tuple: File paths of the saved JSON files containing the schema (section headings) and filled data
             (extracted text and tables).

    Details:
    Opens the PDF, iterates through its ToC to identify sections, extracts text and tables from each section,
    processes the data, and saves it in JSON format. Utilizes helper functions for specific tasks like
    extracting data between pages and replacing tables in text.
    """

    doc = fitz.open(doc_filepath)
    print(f"Fitz document was opened:\n{doc}")
    toc = create_toc(doc)
    print(f"ToC was created:\n{toc}")
    schema = {}
    filled = {}
    i = 0
    for prev_section, curr_section, next_section in toc_iterator(toc):
        print(curr_section)
        print(1)
        sec_num, sec_text, curr_section_page = curr_section
        i += 1  # Increment i for each valid section
        print(3)
        schema[sec_num] = sec_text
        full_text = doc[curr_section_page - 1].get_text()
        tables = [
            (t.header.names, t.extract())
            for t in doc[curr_section_page - 1].find_tables()
        ]
        if next_section:
            print(4.1)
            _, _, next_section_page = next_section
            if next_section_page - curr_section_page > 0:
                full_text, tables = get_between_section_text_and_tables(
                    curr_section_page, next_section_page, doc
                )
        else:
            print(4.2)

        section_inbetween_text = determine_inbetween_text(
            f"{sec_num} {sec_text}",
            f"{next_section[0]} {next_section[1]}" if next_section else "",
            full_text,
        )
        for tab_tuple in tables:
            section_inbetween_text = replace_tables_in_section(
                section_inbetween_text, tab_tuple
            )

        filled[sec_num] = section_inbetween_text

    print(f"{i} iterations over toc_iterator(toc)")

    output_filename = os.path.basename(os.path.splitext(doc_filepath)[0]).replace(
        " ", "_"
    )

    schema_fp, filled_fp = save_to_json(output_filename, output_folder, schema, filled)

    return schema_fp, filled_fp
