"""
Module: templates.task_builder.llm_helper_funcs

This module provides a collection of helper functions specifically designed to support the `InteractiveDocumentTemplate` class within the interactive template builder framework. These functions facilitate key operations such as gathering user input, assessing document files within a specified directory, and extracting content samples from documents to inform the dynamic generation of tasks for interactive document drafting and analysis.

Functions:
    interactive_input_handler(question: str) -> tuple:
        Captures user input in response to a given question, simulating an LLM-like interaction. This function is critical for acquiring nuanced user preferences and requirements that guide the customization of the document drafting tasks.

    os_file_info_handler(directory: str = "input") -> dict:
        Evaluates files within the specified directory, summarizing essential information such as file count, formats, and sizes. This function lays the groundwork for document content analysis by providing a preliminary overview of the available data.

    document_sampler_handler(directory: str = "input", sample_count: int = 5) -> str:
        Randomly selects documents from the specified directory and extracts text samples, particularly supporting PDFs and potentially other formats. This sampling is instrumental in gauging the content's nature and scope, serving as a basis for tailoring subsequent drafting tasks to the document's specific needs.

Usage Scenario:
These helper functions are integral to the operation of the `InteractiveDocumentTemplate`, enhancing its ability to interactively engage with users and utilize the content of documents in the drafting process. By leveraging these functions, the template builder can dynamically generate tasks that are directly informed by user goals and the specific content of the documents under consideration.
"""

# TODO: Use the ToolImplementations class for the tools.

import os

def interactive_input_handler(question):
    user_input = input(f"{question}: ")
    # Simulate LLM response based on user input (replace with actual LLM call)
    llm_response = f"LLM simulated response based on '{user_input}'"
    print(f"LLM says: {llm_response}")
    return user_input, llm_response


def os_file_info_handler(directory="input"):
    if not os.path.exists(directory):
        print("The directory does not exist.")
        return {}
    files = os.listdir(directory)
    file_info = {"formats": set(), "count": len(files), "sizes": [], "total_size": 0}
    for file in files:
        filepath = os.path.join(directory, file)
        file_info["formats"].add(os.path.splitext(file)[1].lower())
        size = os.path.getsize(filepath)
        file_info["sizes"].append(size)
        file_info["total_size"] += size

    print(
        f"Found {file_info['count']} file(s) in '{directory}' with total size {file_info['total_size']} bytes."
    )
    for fmt in file_info["formats"]:
        print(f" - File format: {fmt}")
    return file_info


import os
import random
# import fitz  # PyMuPDF

# TODO -> TBD

# def document_sampler_handler(directory="input", sample_count=5):
#     files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
#     sampled_files = random.sample(files, min(len(files), sample_count))
#
#     for file in sampled_files:
#         file_path = os.path.join(directory, file)
#         print(f"Sampling text from {file}...")
#         try:
#             if file.lower().endswith('.pdf'):
#                 with fitz.open(file_path) as doc:
#                     text_samples = []
#                     for _ in range(min(3, len(doc))):  # Sample up to 3 pages
#                         page = doc[random.randint(0, len(doc) - 1)]
#                         text_samples.append(page.get_text())
#                     sampled_text = "\n---\n".join(text_samples)
#                     print(f"Sampled Text from {file}:\n{sampled_text}\n")
#             # Additional conditions for other file formats (DOCX, etc.) can be added here
#         except Exception as e:
#             print(f"Error processing {file}: {e}")
#     return "Completed sampling text data."
