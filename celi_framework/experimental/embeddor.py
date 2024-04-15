"""
This module, celi_framework.embeddor, is tailored for embedding pre-cleaned text data from source documents. It takes the cleaned output from the celi_framework.pre-processor module and applies further text data analysis and embedding processes, making the data ready for machine learning models and data analysis tools. Key functionalities include:

- Summarizing extensive text sections pre-cleaned by celi_framework.pre-processor to ensure efficient embedding.
- Filtering 'filled' dictionaries, cleaned by celi_framework.pre-processor, against a 'flat schema' to ensure only relevant information is embedded.
- Chunking cleaned text data into manageable sizes for detailed analysis and summarizing oversized chunks when necessary.
- Creating dataframes from chunked text data, applying token counting to manage embedding load, and then embedding the text for further analysis.
- Automating the embedding process for multiple documents, leveraging the celi_framework.pre-processor's output to create well-structured dataframes for analytical tasks.

The module's focus is on transforming cleaned and standardized text data into embedded vectors, utilizing OpenAI's embeddings, suitable for a wide range of machine learning applications.

TODO: Consider refactoring for optimized integration with the pre-processed data.
"""

from celi_framework.experimental.utils.ada import (
    get_openai_embedding_sync_timeouts,
    chunk_text,
)
from celi_framework.utils.token_counters import token_counter_og
from celi_framework.utils.llms import quick_ask
from celi_framework.utils.utils import load_json, save_json
import os
import pandas as pd


def summarize_long_sections(text):
    """
    Summarizes a long section of text.

    Args:
        text (str): Text to be summarized.

    Returns:
        str: Summarized text.
    """

    prompt = f"summarize this chunk of text from a [ENTER DOC TYPE] document succinctly:\n{text}"  # TODO-> Fill in doc type
    response = quick_ask(prompt)
    return response


def filter_dict_based_on_schema(full_text_filepath, schema_filepath):
    """
    Filters a 'filled' dictionary based on a 'flat schema' dictionary, ensuring that only the
    sections specified in the schema are retained for further processing, such as embedding.
    This step is critical in aligning the text data with the expected structure before it undergoes
    embedding by models which require specific input formats.

    Args:
        full_text_filepath (str): Path to the 'filled' dictionary containing pre-processed text.
        schema_filepath (str): Path to the 'flat schema' dictionary which defines the required structure.

    Returns:
        dict: A dictionary filtered to match the structure dictated by the 'flat schema'.
    """

    # Load the pre-processed text data; this data has been cleaned and is ready for embedding
    full_text_dict = load_json(full_text_filepath)

    # Load the schema dictionary which outlines the structure and sections expected for embedding
    schema_dict = load_json(schema_filepath)

    # Retrieve the section keys defined in the schema; these are the only sections we want to keep
    keys_to_keep = schema_dict.keys()

    # Create a new dictionary by filtering out sections that are not present in the schema
    # We go through each key defined in the schema and check if it exists in the full text data
    # If it does, we add it to our new filtered dictionary
    filtered_dict = {
        key: full_text_dict[key] for key in keys_to_keep if key in full_text_dict
    }

    # Save the newly created filtered dictionary back to the file system
    # This overwrites the full text data with our newly filtered content, which is now ready for embedding
    save_json(filtered_dict, full_text_filepath)

    # Return the filtered dictionary for further use, potentially in embedding processes
    return filtered_dict


def chunked_dict(
    dict_filepath,
    dict_dir,
    token_counter,
    schema_keys,
    max_tokens=500,
    chunk_size=250,
    overlap=50,
):
    """
    Splits the text of each section in a dictionary into smaller chunks suitable for text embedding.
    Long sections can be summarized to ensure that the size of each chunk remains within the limits
    set for token count. The aim is to prepare the text for embedding processes where large text
    sizes can be problematic.

    Args:
        dict_filepath (str): Path to the dictionary file containing pre-cleaned text sections.
        dict_dir (str): Directory where the dictionary file is located.
        token_counter (func): Function to count tokens in text to manage embedding sizes.
        schema_keys (list): List of keys that identify sections based on a pre-defined schema.
        max_tokens (int): Maximum number of tokens allowed per chunk to comply with embedding model limits.
        chunk_size (int): Desired size of each text chunk for consistent embedding.
        overlap (int): Number of characters to overlap between chunks to maintain context.

    Returns:
        list: A list of dictionaries containing chunked text data including the document name,
              section identifier, content, and chunk number for further processing.
    """

    # Load the pre-cleaned dictionary file that contains the text to be chunked
    data_dict = load_json(f"{dict_dir}/{dict_filepath}")

    # Extract the base name of the document for labeling purposes
    document_name = dict_filepath.rsplit("_filled_cleaned_for_embed.json", 1)[0]

    # Initialize an empty list to store the results of the chunking process
    chunked_data = []

    # Dictionaries to store summarized sections if necessary
    summarized_whole_section = {}
    summarized_chunk_section = {}

    # Iterate through each section in the dictionary
    for key, value in data_dict.items():
        # Skip sections that are not listed in the provided schema keys
        if key not in schema_keys:
            continue

        # Use the chunk_text function to divide the text into smaller parts
        chunks = chunk_text(value, chunk_size, overlap, token_counter)

        # Handle empty sections by appending a placeholder
        if len(chunks) == 0:
            chunked_data.append([document_name, key, "[Empty Section]", "1"])
            continue

        # If the number of chunks is too large, summarize the whole section
        if len(chunks) > 30:
            summary = summarize_long_sections(value)
            chunked_data.append([document_name, key, summary, "1"])
            summarized_whole_section[key] = summary
            continue

        # Iterate through each chunk
        for idx, chunk in enumerate(chunks, start=1):
            # Count the number of tokens in the chunk to ensure it's within the max_tokens limit
            real_token_count = token_counter_og(chunk)

            # If the token count is within the limit, add the chunk to chunked_data
            if real_token_count <= max_tokens:
                chunked_data.append([document_name, key, chunk, f"{idx}"])
            # If the token count exceeds the limit, summarize the chunk
            else:
                summary = summarize_long_sections(chunk)
                chunked_data.append([document_name, key, summary, f"{idx}"])

                # Record the summarized chunk in the summarized_chunk_section
                if key not in summarized_chunk_section:
                    summarized_chunk_section[key] = {}
                summarized_chunk_section[key][idx] = summary

    # Return the list of chunked and potentially summarized text data
    return chunked_data


def create_df_data(
    dict_dir, df_dir, schema_filename, full_text_filename, approx_token_counter_func
):
    """
    Creates a dataframe from pre-processed and chunked text data, then saves it for embedding analysis.
    This function forms part of the celi_framework.embeddor module, which takes cleaned text data as input,
    typically generated by the celi_framework.pre-processor module, and prepares it for embedding.

    Args:
        dict_dir (str): Directory containing the dictionaries with pre-processed text by celi_framework.pre-processor.
        df_dir (str): Directory where the dataframes, ready for embedding, will be saved.
        schema_filename (str): Filename of the schema, which is used for structuring the chunked text data.
        full_text_filename (str): Filename of the full text that has been cleaned and is to be chunked.
        approx_token_counter_func (func): Function to approximate token counts for managing embedding sizes.

    The function reads the schema and cleaned text, chunks the text based on the schema, and counts the tokens
    for each chunk. It compiles this information into a dataframe, which includes embeddings ready for
    downstream machine learning tasks.
    """

    # Load the schema which dictates the structure of the text data
    schema_dict = load_json(f"{dict_dir}/{schema_filename}")
    schema_keys = schema_dict.keys()

    # Chunk the cleaned text data according to the schema
    chunked_data = chunked_dict(
        full_text_filename, dict_dir, approx_token_counter_func, schema_keys
    )

    # Create a dataframe from the chunked text data
    df = pd.DataFrame(
        chunked_data, columns=["Document", "Section", "Content", "Chunk_Num"]
    )

    # Apply the token counting function to manage the size of embeddings
    df["token_count"] = df["Content"].apply(lambda x: token_counter_og(x))

    # Print token count statistics for review
    print(df["token_count"].describe())
    top_5_rows = df.nlargest(5, "token_count")
    print(top_5_rows)

    # Apply embeddings to the content of each chunk
    df["embedding"] = df["Content"].apply(
        lambda x: get_openai_embedding_sync_timeouts(x, model="text-embedding-ada-002")
    )

    # Construct the filename for the saved dataframe
    document_name = schema_filename.rsplit("_schema.json", 1)[0]

    # Save the dataframe with embeddings to the specified directory
    df.to_csv(f"{df_dir}/{document_name}.csv", index=False)


def loop_through_dicts_to_df(dict_dir, df_dir, token_counter_func):
    """
    Iterates through pre-cleaned dictionaries within a specified directory to create and save dataframes suitable for embedding.
    Each dictionary is assumed to be the output of a text cleaning process, ready for embedding by the celi_framework.embeddor module.
    This function is part of the celi_framework.embeddor module and depends on the output of the celi_framework.pre-processor module.

    Args:
        dict_dir (str): Directory containing cleaned dictionaries prepped by celi_framework.pre-processor.
        df_dir (str): Directory where the resulting dataframes, ready for embedding, will be saved.
        token_counter_func (func): Function to count tokens, used for managing embeddings.

    The function identifies dictionaries based on a naming pattern that indicates they have been cleaned and are ready for embedding.
    It then processes each dictionary to create a dataframe with chunked text and token counts, preparing it for embedding analysis.
    """

    # Identify unique prefixes for filenames indicating they have been cleaned and are ready for embedding
    prefixes = set(
        [
            f.split("_filled_cleaned_for_embed.json")[0]
            for f in os.listdir(dict_dir)
            if "_filled_cleaned_for_embed.json" in f
        ]
    )

    # Process each dictionary file based on its prefix
    for prefix in sorted(prefixes):
        # Construct filenames for the schema and the cleaned text based on the prefix
        schema_filename = f"{prefix}_schema.json"
        full_text_filename = f"{prefix}_filled_cleaned_for_embed.json"

        # Call the function to create and save a dataframe for each cleaned dictionary
        # This function will chunk the text, count the tokens, and apply the embedding
        create_df_data(
            dict_dir, df_dir, schema_filename, full_text_filename, token_counter_func
        )


if __name__ == "__main__":
    """
    This is the main function that will be executed when the script is run directly.
    """

    # Specify the directory containing the dictionaries
    dict_dir = "/path/to/dictionaries"

    # Specify the directory where the dataframes will be saved
    df_dir = "/path/to/dataframes"

    # Specify the token counter function to be used
    token_counter_func = token_counter_og

    # Call the loop_through_dicts_to_df function to process multiple dictionaries and create dataframes for analysis
    loop_through_dicts_to_df(dict_dir, df_dir, token_counter_func)
