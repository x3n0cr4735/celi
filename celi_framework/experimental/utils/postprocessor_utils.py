"""
The postprocessor_utils.py module provides a suite of functions for post-processing tasks on structured document data. It includes functionalities to aggregate JSON data from multiple directories, identify missing sections in document drafts, map these sections to specific headings, and detect sections containing tables. This module is crucial for ensuring the completeness and accuracy of document drafts across various types of structured documents.

Key Functionalities:
- Aggregating JSON data from multiple directories based on specific keywords.
- Identifying missing sections in aggregated document data.
- Mapping missing sections to their respective headings.
- Detecting sections within document drafts that contain tables.

TODOs for Module Improvement:
- Enhance the module's scalability to manage larger datasets and more complex directory structures.
- Implement comprehensive error handling and logging to boost the robustness of the module.
- Develop unit tests to confirm the reliability and accuracy of the module's functionalities.
- Optimize the functions' performance, especially for processing large-scale data.
- Explore integrating more advanced text analysis techniques for post-processing tasks.
"""

import sys

sys.path.append("/path/to/your/project/")

import os
import json
import re
from collections import OrderedDict


def find_missing_sections(collated_data, schema_path, filled_data_path):
    """
    Function to identify missing sections in the collated data based on a schema and check if they have
    empty values in a separate filled data.

    Parameters:
    - collated_data (dict): The combined data from all the JSON files.
    - schema_path (str): Path to the schema JSON file.
    - filled_data_path (str): Path to the filled data JSON file.

    Returns:
    - list: List of missing section numbers from the collated data that have empty values in the filled data.
    """

    # Load the schema
    with open(schema_path, "r") as f:
        schema_json = json.load(f)

    # Load the filled data
    with open(filled_data_path, "r") as f:
        filled_data = json.load(f)

    # Identify sections missing from the collated data
    missing_sections = [
        section for section in schema_json.keys() if section not in collated_data
    ]

    # Filter out sections that don't have empty values in the filled data
    missing_empty_sections = [
        section for section in missing_sections if not filled_data[section] == ""
    ]

    return missing_empty_sections


def map_missing_sections_to_headings(missing_sections, schema_path):
    """
    Maps missing section numbers to their headings based on the schema.

    Parameters:
    - missing_sections (list): List of missing section numbers.
    - schema_path (str): Path to the schema JSON file.

    Returns:
    - dict: Dictionary with section numbers as keys and headings as values.
    """

    # Load the schema
    with open(schema_path, "r") as f:
        schema_json = json.load(f)

    # Create a dictionary mapping missing sections to their headings
    missing_sections_with_headings = {
        section: schema_json.get(section, "No heading found")
        for section in missing_sections
    }

    return missing_sections_with_headings


def sections_with_tables(collated_data):
    """
    Function to identify sections in the collated data that have tables.

    Parameters:
    - collated_data (dict): The combined data from all the JSON files.

    Returns:
    - list: List of section numbers from the collated data that have tables.
    """
    return list(collated_data.keys())


def reverse_map_document_sections_with_headings(
    document_data, reference_material_headings, guidelines_headings
):
    """
    Reverse maps document sections to their sources in reference materials and guidelines with headings.

    Parameters:
    - document_data (dict): The document data with source mappings.
    - reference_material_headings (dict): The section headings of reference materials.
    - guidelines_headings (dict): The section headings of guidelines documents.

    Returns:
    - dict: Dictionary with reference materials and guidelines sections as keys and lists of document sections with headings as values.
    """
    reverse_mapping = {}

    for document_section, details in document_data.items():
        document_heading = details.get("section_heading", "No heading found")
        source_mapping = details.get("source_mapping", {})

        for source, sections in source_mapping.items():
            for section, _ in sections.items():
                if source == "New Reference Material":
                    section_heading = reference_material_headings.get(
                        section, "No heading found"
                    )
                elif source == "New Guidelines":
                    section_heading = guidelines_headings.get(
                        section, "No heading found"
                    )
                else:
                    continue  # skip if the source is not recognized

                mapping_info = {
                    "document_section": document_section,
                    "document_heading": document_heading,
                    "source_section_heading": section_heading,
                }

                source_key = f"{source} {section}"
                reverse_mapping.setdefault(source_key, []).append(mapping_info)

    return reverse_mapping
