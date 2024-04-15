"""
A module for processing PDF documents to extract and manage structured data. This module is designed to be versatile,
supporting various types of PDF documents. It utilizes the PyMuPDF library for document interaction, pandas for data
manipulation, and pickle for data persistence.

In contrast to the other PDF extraction module (pdf_extractor.py), we don't make assumptions here about anything
except the tables themselves (mostly formatting).

Capabilities include:
- Enhancing the readability of data presentations.
- Extracting identifiable information based on customizable patterns.
- Converting document tables into structured pandas DataFrames.
- Serializing processed data for efficient storage and retrieval.

This tool is suitable for any sector requiring automated PDF document management and data extraction, from academic
research to financial analysis.

Functions:
    set_pandas_display_options(): Optimizes display settings for DataFrame output.
    extract_id_from_doc(doc, pattern): Retrieves identifiers from documents using regular expressions.
    process_table(table): Transforms table data into a cleaned DataFrame format.
    extract_tables(doc): Compiles all document tables into a navigable dictionary format.
    get_tables_as_string(tables_list, all_tabs): Produces textual representations of specified tables.
    save_tables(all_tabs, filename): Stores table data persistently.
    load_tables(filename): Reloads stored table data.
    preprocess(doc_fp): Initiates document processing for data extraction and serialization.
    preprocess_all_files_in_directory(directory): Applies preprocessing to all PDF files within a directory.

Example usage:
    Suitable for automating data extraction from PDFs, enhancing data handling workflows in any organization.
"""



import os
import pickle
import re
from io import StringIO
import fitz  # PyMuPDF
import pandas as pd
from dotenv import load_dotenv

from celi_framework.utils.log import app_logger as logger


load_dotenv()

ROOT_DIR = os.getenv("ROOT_DIR")

def set_pandas_display_options():
    """Set pandas display options for better dataframe visualization."""
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)

def extract_id_from_doc(doc, pattern):
    """Extract and return an identifier based on a regex pattern from the document.

    This function searches each page of the document for the specified pattern,
    returning the first match as a tuple of captured groups. If no match is found,
    it returns a tuple of 'UNKNOWN'.

    Args:
        doc (fitz.Document): The document from which to extract data.
        pattern (str): A regex pattern used to identify the desired information.

    Returns:
        tuple: A tuple containing the matched groups, or ('UNKNOWN', 'UNKNOWN') if no match is found.
    """
    for page in doc:
        text = page.get_text()
        found = re.search(pattern, text)
        if found:
            return found.group(1), found.group(2)
    return "UNKNOWN", "UNKNOWN"

def process_table(table):
    """
    Process and return a dataframe from table data, adjusting headers and indexes,
    excluding page headings from being used as table headers. This version keeps the
    naming convention intact and ensures column names are correctly set.

    Returns the cleaned table name to be used as a key and the processed DataFrame.
    """
    df = pd.DataFrame(table.extract())

    # Define a pattern that matches unwanted headings or non-table content
    unwanted_heading_pattern = re.compile(r"----ADD_YOUR_PATTERN----")

    table_name_row_index = None
    header_row_index = None

    # Iterate through each row to find the first row not matching the unwanted pattern
    # and the subsequent row, which will contain the column headers
    for index, row in df.iterrows():
        if table_name_row_index is None and not unwanted_heading_pattern.search(str(row[0])):
            table_name_row_index = index
            continue  # Continue to the next iteration to find the header row
        if table_name_row_index is not None and header_row_index is None:
            header_row_index = index
            break  # Break after finding the header row immediately after the table name row

    # Extract table name and adjust DataFrame to use correct headers
    if table_name_row_index is not None and header_row_index is not None:
        table_name = df.iloc[table_name_row_index][0]  # Use the first cell of the table name row as the table name
        # Clean up the table name
        table_name = table_name.replace('\n', ' ').strip()

        df = df.iloc[header_row_index:]  # Include the header row for column names
        df.columns = df.iloc[0]  # Set the header row as column names
        df = df[1:]  # Remove the header row from the data
    else:
        # Fallback if no suitable rows are found
        table_name = "Unknown_Table"
        df.columns = df.iloc[0]  # Use the first row as a fallback for column names
        df = df[1:]

    df.columns = df.columns.str.replace('\n', ' ', regex=False)  # Clean up column names
    df.reset_index(drop=True, inplace=True)  # Reset the dataframe index

    return table_name, df

def extract_tables(doc):
    """
    Extract tables from the document and return them in a dictionary with keys based on the detected table names.
    """
    all_tabs = {}
    for page in doc:
        for table in page.find_tables():
            table_name, df = process_table(table)
            if table_name in all_tabs:
                all_tabs[table_name].append(df)
            else:
                all_tabs[table_name] = [df]
    return all_tabs

def get_tables_as_string(tables_list, all_tabs):
    """Generate and return a string representation of tables specified in tables_list."""
    output = StringIO()
    for table in tables_list:
        try:
            num_tables = len(all_tabs[table])
            for i in range(num_tables):
                title = f"{table} ({i + 1} of {num_tables}):" if num_tables > 1 else f"{table}:"
                output.write(f"{title}\n{all_tabs[table][i].to_string()}\n\n")
            logger.info(f"Loaded table {table} for context augmentation", extra={'color': 'cyan'})
        except:
            logger.error(f"Could not load table {table}")
    return output.getvalue()

def save_tables(all_tabs, filename):
    """Save the all_tabs object to a file using pickle."""
    with open(filename, 'wb') as f:
        pickle.dump(all_tabs, f)

def load_tables(filename):
    """Load and return the all_tabs object from a file."""
    with open(filename, 'rb') as f:
        return pickle.load(f)

# Other defined functions remain unchanged

def preprocess(doc_fp):
    # doc_fp = f"{ROOT_DIR}/data/project_data/narratives/input/{doc_f}"
    save_pickle_path = f'add/your/path'

    logger.info(f"Pre-processing file: {doc_fp}", extra={'color': 'orange'})
    set_pandas_display_options()
    doc = fitz.open(doc_fp)
    pattern = re.compile(r"----ADD_YOUR_PATTERN-----", re.MULTILINE)
    id = extract_id_from_doc(doc, pattern)
    all_tabs = extract_tables(doc)

    # Construct the file path
    filename = os.path.join(save_pickle_path, f'Profile-{id}.pkl')

    # Save the all_tabs object to the specified path
    save_tables(all_tabs, filename)
    logger.info(f"Saved pre-processed tables to: {filename}", extra={'color': 'orange'})

def preprocess_all_files_in_directory(directory):
    """
    Processes each PDF file within the specified directory, applying data extraction and serialization routines.

    This function is designed to automate the preprocessing of large volumes of PDF files, making it ideal for situations
    where manual data entry would be inefficient or error-prone.

    Args:
        directory (str): The path to the directory containing the PDF files to process.
    """
    # List all files in the directory
    for filename in os.listdir(directory):
        # Create the full file path
        file_path = os.path.join(directory, filename)

        # Check if it's a file and not a directory
        if os.path.isfile(file_path):
            # Call the preprocess function on each file
            preprocess(file_path)

def get_profile_tables(id, tables_list,
                       save_pickle_path=f'add/your/path'):
    # Construct the file path from which to load
    filename = os.path.join(save_pickle_path, f'Profile-{id}.pkl')
    all_tabs = load_tables(filename)
    # print(all_tabs.keys())
    # print(all_tabs)
    tables_string = get_tables_as_string(tables_list, all_tabs)
    return tables_string

if __name__ == "__main__":
    profiles_dir = f"add/your/path"
    preprocess_all_files_in_directory(profiles_dir)
