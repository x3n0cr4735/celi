"""
The `utils.retrieval` module encompasses functionalities for retrieving and processing source material related to document drafting, particularly focusing on mapping and identifying essential sections from source documents. It's designed to support the automation of document analysis tasks, enhancing the drafting process by providing a structured approach to source material retrieval and analysis.

This module integrates with various utility functions and custom parsing mechanisms to facilitate the efficient processing of document data. It aims to streamline the workflow of identifying, mapping, and analyzing document sections, thereby contributing to the accuracy and completeness of document drafts.

Classes:
    EssentialSourceFacade: Manages the retrieval and analysis of essential source materials for document sections. It provides methods to map document sections to source materials, pre-compute essential sources, and save the results for further processing.

Key Functionalities:
- Mapping document sections to corresponding source document sections.
- Pre-computing essential sources for document sections and retrying for failed sections.
- Saving pre-computed essential source mappings and error lists for document drafting and analysis.

TODOs for Module Improvement:
- Enhance scalability to accommodate larger datasets and more complex structures.
- Implement comprehensive error handling and logging for improved robustness.
- Develop unit tests to verify the functionalities' reliability and accuracy.
- Optimize performance for handling large-scale data efficiently.
- Explore advanced text analysis techniques to refine post-processing tasks.

The module serves as a foundational tool for automating the identification and analysis of source materials, ensuring that document drafts are both complete and accurate.
"""

from celi_framework.experimental.utils.mapper_utils import (
    map_document_to_sources_from_json,
    source_material_getter,
)
from celi_framework.utils.utils import (
    load_json,
    save_json,
    write_string_to_file,
    remove_file_extension,
)
from celi_framework.utils.log import app_logger
import os


class EssentialSourceFacade:
    def __init__(
        self,
        fill_dict,
        csv_dir,
        csv_names,
        top_n=7,
        include_content=False,
        checkpoint_dir="checkpoints",
    ):
        """
        Initializes the facade with the directory of dataframes for source documents.
        """
        self.fill_dict = fill_dict
        self.csv_dir = csv_dir
        self.csv_names = csv_names
        self.top_n = top_n
        self.include_content = include_content
        self.mappings = None
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def map_target_to_sources(self):
        self.mappings = map_document_to_sources_from_json(
            self.fill_dict,
            self.csv_dir,
            self.csv_names,
            self.top_n,
            self.include_content,
        )

    def compute_essential_sources(self, retry_rounds=1):
        """
        Pre-computes, stores, and retries for failed sections essential sources for all
        target document sections across n rounds.

        Loads from a checkpoint and saves progress to the same checkpoint directory.
        """

        checkpoint_filepath = os.path.join(self.checkpoint_dir, "checkpoint.json")

        # Attempt to load the existing checkpoint if available
        existing_sections = {}
        if os.path.exists(checkpoint_filepath):
            try:
                existing_sections = load_json(checkpoint_filepath)
                print(f"Loaded checkpoint from {checkpoint_filepath}")
            except Exception as e:
                print(f"Error loading checkpoint: {e}")

        # Determine sections not yet processed
        sections_to_process = {
            k: v for k, v in self.fill_dict.items() if k not in existing_sections
        }
        err_sections = []

        for round in range(retry_rounds + 1):
            for section in sections_to_process.keys():
                app_logger.info(
                    "Commencing essential source pre-computations...",
                    extra={"color": "orange"},
                )
                app_logger.info(f"Running Section {section}", extra={"color": "orange"})
                text_response = source_material_getter(
                    section
                )  # Your actual processing logic
                try:
                    error_parse = parse_completion_for_error_with_llamacpp_parser(
                        text_response
                    )
                    app_logger.info(
                        f"Section {section} parse_completion_for_error:\n{error_parse}",
                        extra={"color": "orange"},
                    )
                    if (
                        error_parse.is_there_a_function_exception
                        or error_parse.is_there_a_function_error
                    ):
                        err_msg = f"Section {section} has Error or exception detected in essential source getter.\n"
                        app_logger.error(err_msg)
                        text_response = err_msg + text_response
                        err_sections.append(section)
                    else:
                        existing_sections[section] = (
                            text_response  # Save successful processing result
                        )
                        app_logger.info(
                            "Error parser: No errors found in source_material_getter response",
                            extra={"color": "orange"},
                        )
                except Exception as e:
                    app_logger.error(
                        f"Could not parse for errors with section {section}: {e}"
                    )
                    if section not in err_sections:
                        err_sections.append(section)

                # Save current progress after each section is processed
                try:
                    save_json(existing_sections, checkpoint_filepath)
                    app_logger.error(
                        "Saved latest checkpoint json for essential source compute!!!"
                    )
                except:
                    app_logger.error(
                        "Could not save latest checkpoint json for essential source compute!!!"
                    )

            # Update sections_to_process for the next round if there are retries
            if round < retry_rounds:
                sections_to_process = {
                    k: self.fill_dict[k]
                    for k in err_sections
                    if k not in existing_sections
                }

        self.essential_section_results = existing_sections
        self.error_sections = err_sections

    def save_pre_computed_essential_sources(
        self, save_filepath="essential_mappings.json"
    ):
        if not self.essential_section_results:
            self.compute_essential_sources()

        save_json(self.essential_section_results, save_filepath)

        root = remove_file_extension(save_filepath)
        err_filepath = root + "_error_list.txt"
        write_string_to_file(str(self.error_sections), err_filepath)


if __name__ == "__main__":
    # Initialize the EssentialSourceFacade class
    fill_dict = {
        "section1": "content1",
        "section2": "content2",
        # Fill this dictionary with the sections you have in your document
    }
    csv_dir = "YOUR_CSV_DIR"
    csv_names = [
        "YOUR_CSV_FILE1.csv",
        "YOUR_CSV_FILE2.csv",
    ]  # Replace with actual CSV files
    facade = EssentialSourceFacade(fill_dict, csv_dir, csv_names)

    # Map tyarget to sources
    facade.map_target_to_sources()

    # Compute essential sources
    facade.compute
