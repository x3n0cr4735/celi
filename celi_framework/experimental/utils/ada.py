"""
ada.py

This module encapsulates functionalities for generating and validating embeddings utilizing the OpenAI API. The provided utilities allow for:
1. Generating embeddings for given text content.
2. Splitting content into manageable chunks based on token limits and overlaps to fit within API constraints.
3. Creating embeddings for structured datasets which include functions, classes, among others.
4. Validating embeddings count and format, ensuring that the generated embeddings are consistent with the provided data.
5. Validating an embedding DataFrame to ensure it adheres to the expected format and content.

These utilities are essential for processing structured data from Python projects, transforming code and textual data into embeddings which can be further used in various downstream tasks including, but not limited to, machine learning, similarity computation, and code analysis.

Author:
    Jan-Samuel Wagner

Usage:
    Import the necessary functions from this module and invoke them with the required arguments. The primary entry point for generating embeddings is the `make_embeddings` coroutine, which can be awaited with the necessary arguments to produce and save the embeddings.

Dependencies:
    - assistant_api: Required for generating embeddings using OpenAI's models.
    - pandas: Essential for handling and storing data in DataFrame format.
    - logging: Utilized for logging runtime information and errors.
    - os and dotenv: Used for managing environment variables which include OpenAI API keys and configuration settings.
    - aiohttp and asyncio: Required for making asynchronous HTTP requests to the OpenAI API, improving the efficiency of embedding generation.

Note:
    Ensure to set the OpenAI API key and other necessary environment variables using a .env file or through other means for correct operation of this module.
"""

import ast
import os
import time


import numpy as np
import openai
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from celi_framework.utils.token_counters import token_counter_og
from celi_framework.utils.log import app_logger

client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_TOKEN_LIMIT = 8100
EMBEDDING_CHUNK_OVERLAP = 500

SAMPLE_SIZE = 50  # Number of samples to determine token-to-length ratio


def chunk_text(text: str, chunk_size: int, overlap: int, token_counter) -> list:
    """Divides a text into overlapping chunks of tokens."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_count = 0

    for word in words:
        current_chunk.append(word)
        current_count += 1

        # When current chunk size reaches the limit, process the chunk
        if current_count == chunk_size:
            chunks.append(" ".join(current_chunk))
            # Move back by 'overlap' words to create the next chunk
            current_chunk = current_chunk[-overlap:]
            current_count = len(current_chunk)

    # Add the last chunk if it contains any words
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def get_openai_embedding_sync_timeouts(
    text: str, model="text-embedding-ada-002", retries=3, timeout=10
) -> list:
    """
    Gets the embedding of a given text using the OpenAI API.

    Args:
        text (str): The text to embed.

    Returns:
        list: The embedding of the text or None if an error occurred.
    """
    text = text.replace("\n", " ")

    for retry in range(retries):
        try:
            if len(text) > 0 and text != "[Empty Section]":
                response = (
                    client.embeddings.create(input=[text], model=model)
                    .data[0]
                    .embedding
                )
                return response
            else:
                return None
        except Exception as e:
            # TODO -> Make into logger error
            app_logger.error(
                f"An error occurred: {e}. Retrying {retry + 1}/{retries}..."
            )
            token_count = token_counter_og(text, api="assistant_api")
            app_logger.error(f"token_count = {token_count}")
            if token_count > 500:
                app_logger.error(f"text = {text[:300]}")
                return None
            time.sleep(1)  # Optional sleep between retries

    return None


def validate_embeddings(df: pd.DataFrame) -> bool:
    """
    Validates the integrity of generated embeddings by comparing a random sample with freshly generated embeddings.

    This function randomly samples embeddings from the provided DataFrame, re-generates embeddings for the
    corresponding content, and compares them to ensure consistency. This validation ensures that the embeddings
    were generated and stored correctly.

    Parameters:
    - embeddings_files (pd.DataFrame): The DataFrame containing 'embedding' and 'content' columns with generated embeddings and
      corresponding content.

    Returns:
    - bool: True if all sampled embeddings match the re-generated embeddings, False otherwise.
    """
    SAMPLE_SIZE = 25

    # Randomly sample 25 rows from the DataFrame
    sample_df = df.sample(n=min(len(df), SAMPLE_SIZE))

    for _, row in sample_df.iterrows():
        original_embedding = row["embedding"]
        regenerated_embedding = get_openai_embedding_sync_timeouts(
            row["content"]
        )  # Assuming 'content' column exists
        if regenerated_embedding != original_embedding:
            app_logger.error("Embeddings do not match!")
            return False

    app_logger.info(
        "Validation successful: All sample embeddings match.", extra={"color": "blue"}
    )
    return True


def validate_embedding_df(df: pd.DataFrame) -> bool:
    """
    Validates the format and content of the embedding DataFrame to ensure it adheres to the expected structure.

    This function iterates through the DataFrame to check for the presence of required columns and validates the format
    of the embeddings. Each embedding should be a list of 1536 elements representing the embedding vector.

    Parameters:
    - embeddings_files (pd.DataFrame): The DataFrame containing the embeddings.

    Returns:
    - bool: True if the DataFrame adheres to the expected format and content, False otherwise.
    """
    required_columns = ["file_path", "item", "embedding"]
    for col in required_columns:
        if col not in df.columns:
            app_logger.error(f"Column '{col}' missing from DataFrame.")
            return False

    for idx, row in df.iterrows():
        try:
            embedding_list = row["embedding"]
            if not isinstance(embedding_list, list) or len(embedding_list) != 1536:
                app_logger.error(
                    f"Invalid embedding at index {idx}. Embedding should be a list of 1536 elements."
                )
                return False
        except (SyntaxError, ValueError):
            app_logger.error(
                f"Invalid embedding format at index {idx}. Embedding should be a string representation of a list."
            )
            return False

    app_logger.info(
        "Embedding DataFrame validation successful.", extra={"color": "blue"}
    )
    return True


#### get_all_embeddings

# load_csv with pandas
# pull columns item, embedding

#### retrienve_similar_documents


def embedding_retriever(query: str, project_hash_id: str) -> list:
    """
    Embeds a query, retrieves the most similar embeddings from the embedding store,
    and returns the items that are the most relevant according to the retriever.

    The function first embeds the input query using the get_openai_embedding_async function.
    It then loads the stored embeddings and their associated items from a CSV file.
    Cosine similarity is computed between the query embedding and all stored embeddings.
    The function returns the items associated with the top 5 most similar embeddings.

    Parameters:
        query (str): The text query to process.
        hash (str): The hash identifier used to locate the embeddings file.

    Returns:
        list: A list of items associated with the top 5 most similar embeddings.
    """

    app_logger.info(
        f"Retrieving similar documents for the query: {query}", extra={"color": "blue"}
    )

    try:
        # Embed the query asynchronously
        query_embedding = get_openai_embedding_sync_timeouts(query)

        # Load stored embeddings and their associated items from a CSV file

        embeddings_file_path = f"/Users/jwag/PycharmProjects/codeshift/src/projects_metadata/{project_hash_id}_items_embeddings.csv"

        df = pd.read_csv(embeddings_file_path)

        # Convert string representation of embeddings back to lists of floats
        df["embedding"] = df["embedding"].apply(lambda x: np.array(ast.literal_eval(x)))

        # Stack embeddings into a 2D numpy array for use with cosine_similarity
        embeddings_matrix = np.vstack(df["embedding"].values)

        # Compute similarity scores between the query embedding and all stored embeddings
        similarity_scores = cosine_similarity([query_embedding], embeddings_matrix)[0]

        # Identify the indices of the top 5 most similar embeddings
        top_indices = np.argsort(similarity_scores)[-5:][::-1]

        # Fetch the items associated with the top 5 most similar embeddings
        items = df.iloc[top_indices][["item", "file_path"]]

        app_logger.info(
            "Successfully retrieved similar documents.", extra={"color": "blue"}
        )
        return items

    except Exception as e:
        # TODO: Make logger error
        app_logger.info(
            f"Error occurred while retrieving similar documents: {e}",
            extra={"color": "blue"},
        )
        return []
