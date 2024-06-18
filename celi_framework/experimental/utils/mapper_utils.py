"""
This Python module, `utils.mapper_utils`, comprises a collection of functions specifically designed for the retrieval and processing of essential information sources for the drafting process of target documents. Its primary objective is to provide contextually relevant and supportive sources, thereby enhancing the efficiency and relevance of the drafting phase.

The module includes several distinct functions, each serving a unique role in the source retrieval process:
- `embed_query()`: This function transforms a given query into an embedded representation for further processing.
- `retrieve_most_similar()`: Given a list of queries, this function retrieves the most similar sections from referenced CSV files.
- `get_relevant_sections_by_section()`: Retrieves relevant sections from a document and its specified reference materials based on a mapping dictionary.
- `get_all_relevant_sections_by_mapping()`: As the name suggests, this function retrieves the relevant sections from a main document and its reference materials for all sections in the document using a mapping dictionary.
- `source_material_getter()`: Based on a document section number, it retrieves relevant source material and constructs a prompt for extended context or subsequent actions.

This module is flexible and readily extendable, which allows it to accommodate different drafting modes, instances, and requirements. Several sections are marked with "TODO" comments indicating potential areas for refactoring and improvements aimed at optimizing the embedding and retrieval processes, increasing modularity, and enhancing code readability and maintainability.

Please ensure all the paths to JSON or CSV files used in this module are correctly set before execution.

As a key component of the document drafting tool, this module significantly contributes to the automation of drafting, thereby improving the overall efficiency of the process.
"""

# TODO: Abstract the embedding and retrieval processes into separate Strategy classes. This will allow for flexible swapping of algorithms and make testing different approaches easier.
# TODO: Implement a factory method for creating different types of embeddings, accommodating various models and approaches in a scalable manner.
# TODO: For each function, assess the feasibility of converting them into class methods, improving modularity and encapsulation.

import ast
import json
import os
from collections import defaultdict, Counter
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from celi_framework.experimental.utils.ada import get_openai_embedding_sync_timeouts
from celi_framework.utils.llms import quick_ask
from celi_framework.experimental.templates import (
    create_prompt_for_essential_section_analysis,
)
from celi_framework.utils.token_counters import get_master_counter_instance
from celi_framework.utils.utils import load_json, get_section_context_as_text
from celi_framework.utils.log import app_logger

TOKEN_LIMIT_PER_MINUTE = 120000


def embed_query(query):
    """
    Placeholder function to embed a query.
    Replace this with your actual embedding function.
    """
    # TODO: Replace with your embedding function
    return get_openai_embedding_sync_timeouts(query, model="text-embedding-ada-002")


# TODO -> Test out this funtion and if you like it add it to the function list in llms.py and then in algorithm
def retrieve_most_similar(queries, csv_dir, csv_names, top_n, include_content):
    """
    Retrieves the most similar rows from the dataframes based on a list of embedded queries.

    :param queries: List of text queries to search for.
    :param df_dir: Directory where the dataframes are stored.
    :param top_n: Number of top similar rows to retrieve for all queries combined.
    :return: Nested JSON where outer keys are document_name and inner keys are section numbers.
    """

    results = defaultdict(dict)
    content_counter = Counter()

    all_similarities = []

    for query in queries:
        query_embedding = np.array(embed_query(query))

        for csv_name in csv_names:
            # Load dataframe
            df_path = os.path.join(csv_dir, csv_name)
            df = pd.read_csv(df_path)

            # Convert string embeddings back to numpy arrays, handle nan values
            df["embedding"] = df["embedding"].apply(
                lambda x: np.array(ast.literal_eval(x)) if pd.notna(x) else np.array([])
            )

            # Determine expected embedding length
            expected_length = 1536

            # Replace empty or missing embeddings with zero-filled array of expected length
            df["embedding"] = df["embedding"].apply(
                lambda x: x if len(x) == expected_length else np.zeros(expected_length)
            )

            # Calculate cosine similarity
            similarities = cosine_similarity(
                query_embedding.reshape(1, -1), list(df["embedding"])
            )

            for idx, similarity in enumerate(similarities[0]):
                all_similarities.append((similarity, df_path, idx))

    # Sort all similarities and pick top_n
    all_similarities = sorted(all_similarities, key=lambda x: x[0], reverse=True)[
        :top_n
    ]

    for similarity, df_path, idx in all_similarities:
        # Load dataframe
        df = pd.read_csv(df_path)

        doc_name = df.iloc[idx]["Document"]
        section_num = df.iloc[idx]["Section"]
        content = df.iloc[idx]["Content"]

        if include_content:
            # Update the counter
            content_counter[(doc_name, section_num)] += 1

            results[doc_name][section_num] = {
                "content": content,
                "count": content_counter[(doc_name, section_num)],
            }
        else:
            # Update the counter
            content_counter[(doc_name, section_num)] += 1

            results[doc_name][section_num] = {
                "count": content_counter[(doc_name, section_num)]
            }

    return results


def map_document_to_sources_from_json(
    document_json, data_dir, data_names, top_n, include_content
):
    """
    Maps sections from a document JSON to their corresponding sections in reference materials.

    :param document_json: JSON containing document sections with section identifiers as keys and text as values.
    :param data_dir: Directory where reference material data are stored.
    :param data_names: Names of the CSV files containing the reference materials.
    :param top_n: Number of top similar entries to retrieve for all queries combined.
    :param include_content: Flag to include content in the results.
    :return: Dictionary mapping document sections to similar sections in reference materials.
    """
    section_mappings = defaultdict(dict)

    # Iterate through each section in the document JSON
    for section_identifier, section_text in document_json.items():
        if len(section_text) > 0:
            print(f"Starting {section_identifier}")
            # Skip empty sections
            if not section_text.strip():
                continue

            # Retrieve most similar sections from reference materials
            similar_sections = retrieve_most_similar(
                queries=[section_text],
                data_dir=data_dir,
                data_names=data_names,
                top_n=top_n,
                include_content=include_content,
            )

            # Map the document section to these similar sections
            section_mappings[section_identifier] = similar_sections
            # Optional logging for each mapping
            # logger.info(f"{section_identifier} mapping: {similar_sections}", extra={'color': 'orange'})

    return section_mappings


def get_relevant_sections_by_section(
    document_section,
    mapping_dict,
    document_content,
    reference_material_content,
    guidelines_content,
    return_document_content,
):
    """
    Retrieves relevant sections from a document and its reference materials based on a mapping dictionary.

    :param document_section: The section identifier in the main document to retrieve.
    :param mapping_dict: The mapping dictionary that links document sections to reference material and guidelines sections.
    :param document_content: Dictionary containing the content of the main document.
    :param reference_material_content: Dictionary containing content of the reference material.
    :param guidelines_content: Dictionary containing content of the guidelines document.
    :return: A dictionary with the content of the relevant sections from the main document, reference material, and guidelines.
    """
    app_logger.info(
        "Retrieval Agent - Utilizing pre-computed data structures for source retrieval...",
        extra={"color": "blue"},
    )
    app_logger.info(
        "Data Structure Traversal - searching for source materials...",
        extra={"color": "orange"},
    )
    relevant_sections = {}

    # Get content from the main document
    if return_document_content:
        toc = load_json("/path/to/document_schema.json")
        relevant_sections["Document"] = (
            f"{get_section_context_as_text(document_section, toc)}"
            f'Content:\n{document_content.get(document_section, "Section not found in the main document")}'
        )

        app_logger.info("relevant_sections['Document']", extra={"color": "cyan"})
        app_logger.info(f"{relevant_sections['Document']}", extra={"color": "cyan"})

    # Get content from reference material and guidelines based on mapping
    for doc, sections in mapping_dict.get(document_section, {}).items():
        if "Reference Material" in doc:
            relevant_sections["Reference Material"] = {}
            ref_toc = load_json("/path/to/reference_material_schema.json")
            for sec in sections:
                context_text = get_section_context_as_text(sec, ref_toc)
                content = reference_material_content.get(
                    sec, "Section not found in reference material"
                )
                relevant_sections["Reference Material"][
                    sec
                ] = f"{context_text}Content:\n{content}"

            app_logger.info(
                "relevant_sections['Reference Material']", extra={"color": "cyan"}
            )
            app_logger.info(
                f"{relevant_sections['Reference Material']}", extra={"color": "cyan"}
            )

        elif "Guidelines" in doc:
            guidelines_toc = load_json("/path/to/guidelines_schema.json")
            relevant_sections["Guidelines"] = {}
            for sec in sections:
                context_text = get_section_context_as_text(sec, guidelines_toc)
                content = guidelines_content.get(sec, "Section not found in guidelines")
                relevant_sections["Guidelines"][
                    sec
                ] = f"{context_text}Content:\n{content}"

            app_logger.info("relevant_sections['Guidelines']", extra={"color": "cyan"})
            app_logger.info(
                f"{relevant_sections['Guidelines']}", extra={"color": "cyan"}
            )

    app_logger.info(
        "Data Structure Traversal - Relevant source sections identified.",
        extra={"color": "orange"},
    )

    return relevant_sections, document_section


def get_all_relevant_sections_by_mapping(
    mapping_dict, document_content, reference_material_content, guidelines_content
):
    """
    Retrieves the relevant sections from a main document and its reference materials for all sections in the document.

    :param mapping_dict: The mapping dictionary that links document sections to reference material and guidelines sections.
    :param document_content: Dictionary containing content of the main document.
    :param reference_material_content: Dictionary containing content of the reference material.
    :param guidelines_content: Dictionary containing content of the guidelines document.
    :return: A dictionary with the content of the relevant sections from the main document, reference material, and guidelines for all document sections.
    """
    all_relevant_sections = {}

    for document_section, mappings in mapping_dict.items():
        relevant_sections = {
            "Document": document_content.get(
                document_section, "Section not found in the main document"
            )
        }

        for doc, sections in mappings.items():
            if "Reference Material" in doc:
                relevant_sections["Reference Material"] = {
                    sec: reference_material_content.get(
                        sec, "Section not found in reference material"
                    )
                    for sec in sections
                }
            elif "Guidelines" in doc:
                relevant_sections["Guidelines"] = {
                    sec: guidelines_content.get(sec, "Section not found in guidelines")
                    for sec in sections
                }

        all_relevant_sections[document_section] = relevant_sections

    return all_relevant_sections


def source_material_getter(section_number):
    text_response = ""

    app_logger.info("Launching Embedding/Retrieval Agent", extra={"color": "blue"})
    json_dir = "path_to_json_files"
    mappings = load_json("path_to_mappings")
    filled = load_json(f"{json_dir}/filled_file")

    def section_text_getter(
        document_name, section_number, doc_dir="path_to_json_files"
    ):
        # Map document names to their respective file paths
        file_paths = {
            "Document A": f"{doc_dir}/file_a",
            "Document B": f"{doc_dir}/file_b",
            "Document C": f"{doc_dir}/file_c",
        }

        # Get the file path for the given document name
        file_path = file_paths.get(document_name)

        # If file path is not found, return an error
        if not file_path:
            return f"Document '{document_name}' not found."

        try:
            # Load the document content
            document = load_json(file_path)
            # Retrieve the requested section text
            text = document.get(section_number, "Section not found.")
            return text if text.strip() else "Empty Section"

        except Exception as e:
            err_msg = (
                f"Error reading section {section_number} from {document_name}: {e}"
            )
            app_logger.error(err_msg)
            return f"{err_msg}"

    # Retrieve the relevant sections based on the mapping dictionary
    relevant_sections, _ = get_relevant_sections_by_section(
        document_section=section_number,
        mapping_dict=mappings,
        content=filled,
        return_content=True,
    )

    # Generate the prompt for section analysis
    prompt = create_prompt_for_essential_section_analysis(relevant_sections)

    # Check if content is present
    if prompt == "No content. Skip.":
        return "ERROR GETTING SOURCE MATERIAL. Proceed to next document section."

    try:
        # Query the model for analysis
        app_logger.info(
            "Retrieval Agent - trimming Trees of source materials...",
            extra={"color": "blue"},
        )

        token_counter = get_master_counter_instance()

        app_logger.info("Calling home to GPT", extra={"color": "yellow"})

        response_str = quick_ask(
            prompt,
            token_counter=token_counter,
            json_output=True,
            timeout=None,
            model_name="gpt-4-turbo-preview",
            time_increase=None,
            max_retries=3,
        )

        app_logger.info("response str came back from quick_ask")

        # Check if response_str is a string and parse it as JSON
        if isinstance(response_str, str):
            app_logger.info("response_str is type str")
            try:
                response = json.loads(response_str)
            except json.JSONDecodeError as e:
                app_logger.error(f"Error parsing response as JSON: {e}")
                app_logger.error(f"Response string: {response_str}")
                response = None
        else:
            app_logger.error("response = response_str")
            response = response_str

        # Now, ensure that response is a dictionary and has the key 'Sufficient Source Material'
        if isinstance(response, dict) and "Sufficient Source Material" in response:
            app_logger.info(
                "isinstance(response, dict) and 'Sufficient Source Material' in response"
            )
        else:
            app_logger.error(
                "Response is not a dictionary or is missing the 'Sufficient Source Material' key."
            )
            app_logger.error(f"Response content: {response}")
    except Exception as e:
        app_logger.error(f"An error occurred: {e}")

    try:
        if response["Sufficient Source Material"]:
            for section in response["sections"]:
                try:
                    content = section_text_getter(
                        document_name="Document A", section_number=section
                    )
                    app_logger.info(
                        f"Reading dictionary for: Document A, Section: {section}",
                        extra={"color": "cyan"},
                    )
                    if len(content) > 0:
                        text_response += (
                            "Document A\n"
                            + "Section "
                            + section
                            + ": "
                            + "\n"
                            + content
                            + "\n"
                        )
                except Exception as e:
                    app_logger.error(f"Error appending section {section}: {e}")

        else:
            text_response = response
            app_logger.error("Text response is set to response")

    except Exception as e:
        bare_err = f"Error during source material retrieval: {e}"
        response_error = f"\nResponse was {response}"
        app_logger.error(f"{response_error}", extra={"color": "red"})
        response_msg = (
            f"{bare_err}\n{response_error}\nIMPORTANT: Trimming to essential source materials was unsuccessful but, for the next tasks, "
            f"just use all the potentially essential source sections below:\n{relevant_sections}.\n"
            f"Run section_text_getter on the potentially essential sections (if you need to) "
            f"and decide what sources are essential.\n"
            f'DO NOT SKIP THE TASK "New sources indexes"\n'
            f'YOU STILL NEED TO DO TASK "New sources indexes"'
        )
        app_logger.info(response_msg, extra={"color": "cyan"})
        return response_msg

    return (
        text_response
        + '\n\n SUCCESS: source_sections_getter function has found the section source materials. \n "Task #4 is complete. Proceed to Task #5 immediately."'
    )
