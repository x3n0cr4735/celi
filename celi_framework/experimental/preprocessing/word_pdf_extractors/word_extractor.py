"""
This script provides functionalities to extract and process content from Microsoft Word (.docx) documents,
specifically targeting sections identified through the Table of Contents (ToC). It is capable of retrieving
text and tables between specified ToC identifiers, converting table data into Markdown format, and organizing
extracted content into a structured format ready for JSON serialization.

Dependencies:
- os.path: For handling file paths.
- docx: For reading and manipulating .docx files.
- pandas: Used for converting table data into Markdown format.
- copy: For creating deep copies of the document tables to prevent modifying the original document.

The script utilizes helper functions from an external module 'extractor_helpers' for navigating between sections
and saving extracted data. It sets the pandas display option to ensure table data is not truncated when converted
to Markdown. A global variable 'paraId_key' is defined to specify the XML namespace used for paragraph IDs, which
are crucial for mapping document elements.

Key Components:
- toc_content_retriever: Retrieves content between two ToC identifiers, including text and Markdown-formatted tables.
- prepare_table_map: Creates a mapping of paragraph IDs to table objects for efficient lookup.
- create_table_md: Converts table objects to Markdown-formatted strings.
- toc_link_cleaner: Parses hyperlink elements to extract ToC keys and values.
- extract_from_word_docx: Orchestrates the extraction process, saving the structured content to JSON files.

The script is designed to be modular and reusable, allowing for the extraction of structured content from
Word documents for various applications, including content management systems, document analysis, and data migration.

Note: docstrings and comments were made by Sam.
"""

import os.path
from docx import Document
import pandas as pd
import copy

from .extractor_helpers import previous_next_helper, save_to_json

pd.set_option('display.max_colwidth', 0)
paraId_key = '{http://schemas.microsoft.com/office/word/2010/wordml}paraId'


def toc_content_retriever(body_elements, table_map, curr_toc_id, next_toc_id):
    """
    Retrieves the content between two Table of Contents (ToC) identifiers in a Word document,
    including text and tables, formatted as Markdown.

    Parameters:
    - body_elements (xml.etree.ElementTree.Element): The XML body elements of the Word document.
    - table_map (dict): A dictionary mapping paragraph IDs to table objects.
    - curr_toc_id (str): The current ToC item's identifier.
    - next_toc_id (str): The next ToC item's identifier.

    Returns:
    - str: A string of concatenated section content including text and Markdown-formatted tables.

    Details:
    Extracts paragraphs and tables located between the specified ToC identifiers by using XPath queries,
    formats tables as Markdown using the `create_table_md` function, and compiles all content into a single string.
    """

    curr_bookmarks_parent_id = \
    body_elements.xpath(f".//w:bookmarkStart[contains(@w:name, '{curr_toc_id}')]/..")[0].attrib[paraId_key]
    next_bookmarks_parent_id = \
    body_elements.xpath(f".//w:bookmarkStart[contains(@w:name, '{next_toc_id}')]/..")[0].attrib[paraId_key]
    content = body_elements.xpath(
        f"//w:*[preceding-sibling::w:p[contains(@w14:paraId, '{curr_bookmarks_parent_id}')] and following-sibling::w:p[contains(@w14:paraId, '{next_bookmarks_parent_id}')]]")

    full_section_text = []
    for elem in content:
        tag = elem.tag.split("}")[1]
        if tag == "p":
            full_section_text.append(elem.text + "\n")
        elif tag == "tbl":
            first_row_paraId = elem.xpath(".//w:tr[1]")[0].attrib[paraId_key]
            if first_row_paraId in table_map:
                full_section_text.append(create_table_md(table_map[first_row_paraId]) + "\n")
    return " ".join(full_section_text)


def prepare_table_map(d_tables):
    """
    Prepares a mapping of paragraph IDs to table objects from the document tables.

    Parameters:
    - d_tables (list): A list of table objects extracted from a Word document.

    Returns:
    - dict: A dictionary where keys are paragraph IDs and values are the corresponding table objects.

    Details:
    Iterates through each table in the document, extracting the paragraph ID of the first row in each table
    and using it as a key in the returned dictionary.
    """

    t_map = {}

    for idx, tbl in enumerate(d_tables):
        first_row_paraId = tbl._tbl.xpath(".//w:tr[1]")[0].attrib[paraId_key]
        t_map[first_row_paraId] = tbl

    return t_map


def create_table_md(xpath_table):
    """
    Converts a table object into a Markdown-formatted string.

    Parameters:
    - xpath_table (Table): A table object extracted from a Word document.

    Returns:
    - str: A string representing the table in Markdown format.

    Details:
    Extracts the text from each cell in the table, arranges the data into rows and columns,
    and uses pandas DataFrame to format the table as Markdown.
    """

    data = []
    keys = None
    for i, row in enumerate(xpath_table.rows):
        text = (cell.text for cell in row.cells)

        if i == 0:
            keys = tuple(text)
            continue
        row_data = dict(zip(keys, text))
        data.append(row_data)
    df = pd.DataFrame(data).to_markdown()
    return str(df)


def toc_link_cleaner(hlink_element):
    """
    Cleans and parses the text of a hyperlink element to extract ToC keys and values.

    Parameters:
    - hlink_element (xml.etree.ElementTree.Element): An XML element representing a hyperlink in the document.

    Returns:
    - tuple: A tuple containing the ToC key and value extracted from the hyperlink text. Returns (None, None) if no numeric key is found.

    Details:
    Splits the hyperlink text on tabs, extracting the numeric key and associated value if present.
    """

    link_text = hlink_element.text
    if link_text[0].isnumeric():
        toc_key, toc_value, *_ = link_text.split("\t")
        return toc_key, toc_value
    else:
        return None, None


def extract_from_word_docx(doc_filepath, output_folder):
    """
    Extracts and processes content from a Word document based on its Table of Contents (ToC), saving the extracted
    content and structure to JSON files in the specified output folder.

    Parameters:
    - doc_filepath (str): The file path to the Word document (.docx).
    - output_folder (str): The directory where the output JSON files will be saved.

    Returns:
    - tuple: File paths of the JSON files containing the structured document schema and extracted content.

    Details:
    Opens the Word document, prepares a map of tables, iterates through hyperlinks to identify ToC sections,
    retrieves content for each section, and saves the structured data in JSON format.
    """

    d = Document(doc_filepath)
    body_elements = d._body._body
    doc_tables = copy.deepcopy(d.tables)
    table_map = prepare_table_map(d_tables=doc_tables)

    hyperlinks = body_elements.xpath(".//w:hyperlink")

    schema = {}
    filled = {}
    for _, curr_hlink, next_hlink in previous_next_helper(hyperlinks):
        toc_key, toc_value = toc_link_cleaner(curr_hlink)
        if toc_key is not None:
            curr_toc_id = curr_hlink.anchor
            next_toc_id = next_hlink.anchor
            toc_section_content = toc_content_retriever(body_elements, table_map, curr_toc_id, next_toc_id)
            schema[toc_key] = toc_value
            filled[toc_key] = toc_section_content

    output_filename = os.path.basename(
        os.path.splitext(doc_filepath)[0]
    ).replace(" ", "_")
    schema_fp, filled_fp = save_to_json(output_filename, output_folder, schema, filled)

    return schema_fp, filled_fp

