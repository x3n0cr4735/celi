"""
The `utils.utils` module encapsulates a variety of utility functions and classes designed to support and enhance
the development of Python applications. This module includes functionalities for colorized logging, JSON and text
file manipulation, dynamic content generation, and more, offering a robust toolkit for developers.

Features:
- Colorized Logging: Utilizes ANSI escape codes to colorize log messages for enhanced readability. Includes a custom
  logging handler (`ColorizingStreamHandler`) that integrates with MongoDB for advanced logging purposes.
- JSON File Manipulation: Provides functions (`load_json`, `save_json`) for loading and saving JSON data, streamlining
  data handling and storage.
- Text Processing: Offers utilities for reading text files (`read_txt`), manipulating JSON objects (`remove_newlines_from_json`,
  `is_json_cleaned_of_newline`), and more, facilitating the processing and analysis of textual data.
- Dynamic Content Generation: Contains methods for generating hash IDs (`generate_hash_id`), creating and manipulating
  data structures (`shuffle_json_ordering`, `transform_dict_to_flat_schema`), and comparing JSON files (`compare_json_files`,
  `detailed_compare_json_files`), aiding in the creation and management of dynamic content.
- File and Directory Operations: Includes functions for working with files and directories (`find_latest_file`,
  `make_list_of_dirs`), enabling efficient file system navigation and organization.
- Miscellaneous Utilities: Offers a variety of additional tools, such as a decorator for measuring function execution
  time (`time_it`), and methods for modifying text and data structures to meet specific criteria (`remove_text_chunk`,
  `dequeue_all_matching`).

Usage:
This module is designed to be imported and used in Python applications that require advanced logging capabilities,
efficient data handling, and manipulation, as well as dynamic content generation. Its modular design allows for
easy integration into existing projects, enhancing functionality without significant refactoring.
"""

import importlib
from pathlib import Path
import random
from datetime import datetime
import hashlib
import time
from functools import wraps
import json
import re
from typing import Optional
import os
import glob


class UnrecoverableException(BaseException):
    pass


def get_obj_by_name(name: str):
    module_path, attr_name = name.rsplit(".", 1)

    # Dynamically import the module and attribute
    module = importlib.import_module(module_path)
    attr = getattr(module, attr_name)
    return attr


def encode_class_type(cls):
    return f"{cls.__module__}.{cls.__name__}"


def load_json(file_path):
    """
    Loads a JSON file from a specified file path and returns its content as a dictionary.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The content of the JSON file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Load and return the JSON data
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def save_json(file, file_path):
    """
    Saves a dictionary to a JSON file at the specified file path.

    Args:
        file (dict): The dictionary to save as JSON.
        file_path (str): Path where the JSON file will be saved.
    """
    with open(file_path, "w") as json_file:
        json.dump(file, json_file)


def read_txt(file_path):
    """
    Reads the entire contents of a text file into a single string.

    Args:
    file_path (str): The path to the file to be read.

    Returns:
    str: A string containing the contents of the file.
    """
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def check_last_line(input_string, string_to_check="[END]"):
    """
    Checks if the last line of the input string is 'Proceed to next section.'

    Args:
    input_string (str): The string to be checked.

    Returns:
    bool: True if the last line is 'Proceed to next section.', False otherwise.
    """
    # Splitting the string into lines
    lines = input_string.split("\n")

    # Checking if the last line is exactly 'Proceed to next section.'
    return lines[-1].strip() == string_to_check


def remove_newlines_from_json(json_obj):
    """
    Removes newline characters from the values in a JSON object.

    Args:
    json_obj (dict): The JSON object from which newline characters will be removed.

    Returns:
    dict: A new JSON object with newline characters removed from values.
    """
    cleaned_json = {}
    for key, value in json_obj.items():
        # Remove \n and \\n from the string value
        cleaned_value = value.replace("\n", "").replace("\\n", "")
        cleaned_json[key] = cleaned_value

    return cleaned_json


def is_json_cleaned_of_newline(json_obj):
    """
    Checks if the JSON object has been cleaned of newline characters.

    Args:
    json_obj (dict): The JSON object to be checked.

    Returns:
    bool: True if the JSON object is free of newline characters, False otherwise.
    """
    for value in json_obj.values():
        if "\n" in value or "\\n" in value:
            return False
    return True


def isolate_last_dict(output):
    """
    Isolates and returns the last dictionary found in a string of concatenated JSON dictionaries.

    Args:
        output (str): The string containing one or more JSON dictionaries.

    Returns:
        dict: The last dictionary found in the string, or None if no dictionary is found.
    """
    # Isolate dictionaries using regex
    dict_strings = re.findall(
        r'\{".+?".+?\}', output.replace("\\n", "").replace("\n", "")
    )

    # Check if there are any matches
    if not dict_strings:
        return None  # or {} if you prefer to return an empty dict when no matches are found

    last_dict_string = dict_strings[-1]
    try:
        # Convert the last string to a dictionary
        dict_obj = json.loads(last_dict_string)
        return dict_obj
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON string: {last_dict_string}")
        print(f"Error message: {e}")
        return None  # or {} if error handling requires an empty dict


def are_jsons_identical(json1, json2):
    """
    Compares two JSON objects to check if they are identical.

    Args:
    json1 (dict): First JSON object.
    json2 (dict): Second JSON object.

    Returns:
    bool: True if the JSON objects are identical, False otherwise.
    """
    json1 = remove_newlines_from_json(json1)
    json2 = remove_newlines_from_json(json2)

    if json1.keys() != json2.keys():
        print("keys are different")

    for key in json1:
        print(key)
        print(f"{json1[key]}---------------\n" f"{json2[key]}")

        if json1[key] != json2[key]:
            print("^^^^^^^ BAD ^^^^^^^^^^")
            print()
            print()


def shuffle_json_ordering(data):
    """
    Randomly shuffles the ordering of keys in a JSON object.

    Args:
        data (dict): The JSON object to shuffle.

    Returns:
        dict: A new JSON object with keys shuffled.
    """
    new_data = {}
    used_numbers = set()

    for i in range(1, 32):
        random_number = random.randint(1, 31)
        while random_number in used_numbers:
            random_number = random.randint(1, 31)

        used_numbers.add(random_number)
        new_data[str(random_number)] = data[str(i)]
    return new_data


# Function to load a text file
def load_text_file(file_path):
    """
    Reads the contents of a text file and returns it as a string.

    Args:
    file_path (str): The path to the text file to be read.

    Returns:
    str: The contents of the file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def transform_dict_to_flat_schema(to_fill_dict):
    """
    Transform the "to be filled" dictionary to a flat schema dictionary.

    Args:
    second_dict (dict): The "to be filled" dictionary with nested structure.

    Returns:
    dict: Transformed dictionary with keys as section numbers and values as section headings.
    """
    transformed_dict = {}
    for key, value in to_fill_dict.items():
        transformed_dict[key] = value["section heading"]
    return transformed_dict


# Another
def transform_dict_to_flat_filled(original_dict):
    """
    Transforms the given dictionary by setting the value to an empty string if 'section body' is
    'Body not present'. If 'section body' has other content, it uses the 'content' field.
    The transformed dictionary will have the same keys, but their values will be either
    the extracted 'content' or an empty string.

    :param original_dict: Dictionary with nested structure containing 'content' and 'section body'
    :return: A new dictionary with keys mapping to 'content' or an empty string
    """
    new_dict = {}

    for key, value in original_dict.items():
        if value.get("section body", "") == "Body not present":
            # Set value to an empty string if 'section body' is 'Body not present'
            new_dict[key] = ""
        elif "content" in value:
            # Use the 'content' value if present and 'section body' is not 'Body not present'
            new_dict[key] = value["content"]
        else:
            # If neither 'section body' nor 'content' are present, set to an empty string
            new_dict[key] = ""

    return new_dict


def filter_empty_sections(toc_dict, content_dict):
    """
    Filters out sections from the table of contents dictionary (toc_dict)
    when the corresponding content in content_dict is empty or only contains newline characters.

    Args:
    toc_dict (dict): Table of contents dictionary.
    content_dict (dict): Content dictionary.

    Returns:
    dict: Filtered table of contents dictionary.
    """
    filtered_toc = {}
    for section, title in toc_dict.items():
        content = content_dict.get(section, "").strip()
        if content:
            filtered_toc[section] = title
    return filtered_toc


def get_section_context_as_text(section_number, toc):
    """
    Retrieves the contextual hierarchy for a given section number from the table of contents
    and formats it as a text block.

    Parameters:
    - section_number (str): The section number to retrieve context for.
    - toc (dict): The table of contents mapping section numbers to headings.

    Returns:
    - str: A formatted text block containing the section number and its contextual headings.
    """
    context_text = "Parent Sections:\n"
    parts = section_number.split(".")

    for i in range(1, len(parts) + 1):
        super_section = ".".join(parts[:i])
        if super_section in toc:
            context_text += f"{super_section}: {toc[super_section]}\n"

    return context_text


def get_parent_section(section_number):
    """
    Returns the parent section number of a given section.
    For example, the parent of '11.5.1.1' would be '11.5.1'.
    """
    parts = section_number.split(".")
    if len(parts) > 1:
        return ".".join(parts[:-1])
    return None  # No parent section exists


def format_toc(toc_dict):
    """
    Formats a table of contents dictionary into a string representation.

    Args:
        toc_dict (dict): The table of contents dictionary.

    Returns:
        str: A formatted string representation of the table of contents.
    """
    formatted_toc = ""
    for section, title in toc_dict.items():
        # Count the dots to determine the hierarchy level (depth)
        depth = section.count(".")
        indent = "    " * depth  # Indentation for each level
        formatted_toc += f"{indent}{section}: {title}\n"
    return formatted_toc


def write_string_to_file(input_string, file_name):
    """
    Writes a given string to a text file.

    Args:
    input_string (str): The string to be written to the file.
    file_name (str): The name of the file where the string will be written.

    Returns:
    None
    """
    with open(file_name, "w") as file:
        file.write(input_string)


def create_new_timestamp(ms=False):
    """
    Generates a new timestamp string.

    Args:
        ms (bool): Whether to include milliseconds in the timestamp. Defaults to False.

    Returns:
        str: The generated timestamp string.
    """
    if ms:
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    else:
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]


def find_latest_file(directory, pattern):
    """
    Find the latest file in a directory matching a given pattern.

    Args:
    directory (str): The path to the directory to search in.
    pattern (str): The pattern to match the filenames against.

    Returns:
    str: Filepath of the latest file matching the pattern. Returns None if no file is found.
    """
    # Join the directory and pattern to create a search path
    search_path = os.path.join(directory, "*" + pattern + "*")

    # List all files matching the pattern
    files = glob.glob(search_path)

    # Find the latest file
    if files:
        latest_file = max(files, key=os.path.getmtime)
        return latest_file

    return None


def read_file_content(filename, directory_path):
    """
    Reads the content of a file given its name and directory path.

    Args:
        filename (str): The name of the file.
        directory_path (str): The path to the directory containing the file.

    Returns:
        str: The content of the file, or an error message if the file cannot be read.
    """
    file_path = os.path.join(directory_path, filename)

    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except IOError as e:
        return f"Error reading file {filename}: {e}"


def read_latest_file_with_pattern(
    dir_path: str, pattern_str: str, extension=".txt"
) -> Optional[str]:
    """
    Reads the content of the latest text file in a given directory that matches a specified regex pattern.

    Args:
    dir_path (str): The path to the directory containing the files.
    pattern_str (str): The regex pattern to match the filenames.

    Returns:
    str: The content of the latest file matching the pattern, or None if no such file is found.
    """
    latest_file = None
    latest_mod_time = 0

    # Append .*\.txt$ to the pattern string to ensure it matches text files
    full_pattern = f"{pattern_str}.*\\{extension}$"

    # Compile the regex pattern from the modified pattern string
    pattern = re.compile(full_pattern)

    # Iterate through all files in the given directory
    for file in os.listdir(dir_path):
        if pattern.match(file):
            file_path = os.path.join(dir_path, file)
            mod_time = os.path.getmtime(file_path)
            if mod_time > latest_mod_time:
                latest_mod_time = mod_time
                latest_file = file_path

    # Read and return the content of the latest file, if any
    if latest_file:
        with open(latest_file, "r") as file:
            return file.read()

    return None


def make_list_of_dirs(list_of_dirs):
    """
    Creates a list of directories if they do not already exist.

    Args:
        list_of_dirs (list): A list of directory paths to create.

    Returns:
        None
    """
    for dir in list_of_dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise ValueError(f"Boolean value expected. Got: {v}")


def generate_hash_id(obj):
    """
    Generates a unique template ID based on the hash of stringable object.

    Args:
        config (stringable type): An object that can be turned into a string to hash.

    Returns:
        str: A unique template ID.
    """
    # Convert the config dictionary to a string and encode it to bytes
    txt_str = str(obj).encode("utf-8")

    # Use SHA256 hash function to generate a hash of the config
    hash_obj = hashlib.sha256(txt_str)

    # Return the hexadecimal representation of the digest
    return hash_obj.hexdigest()


def generate_prompt_and_completion_id(
    system_message, ongoing_chat, prompt_completion=None, timestamp=None
):
    """
    Generates a unique hash ID for the document based on the system message,
    user message, prompt completion, and timestamp.

    Args:
        system_message (str): The system message content.
        user_message (str): The user message content.
        prompt_completion (str): The prompt completion content.
        timestamp (str): The exact timestamp up to milliseconds.

    Returns:
        str: A unique hash ID for the document.
    """
    # Concatenate the input strings with the timestamp
    combined_string = (
        system_message
        + ongoing_chat
        + (prompt_completion if prompt_completion is not None else "")
        + (timestamp if timestamp is not None else "")
    )
    # Encode the combined string to bytes
    encoded_string = combined_string.encode("utf-8")
    # Create a hash object and generate the hash
    hash_obj = hashlib.sha256(encoded_string)
    # Return the hexadecimal representation of the digest
    return hash_obj.hexdigest()


def generate_task_specific_id(document_type, section_number, task):
    """
    Generates a unique hash ID based on the master template ID, section number, and task number.

    Args:
        master_template_id (str): The ID of the master template.
        section_number (str): The current section number being processed.
        task_number (str): The current task number being processed.

    Returns:
        str: A unique hash ID for identifying a specific task within a document.
    """

    # Ensure all inputs are converted to strings
    section_number_str = str(section_number)
    task_str = str(task)

    # Concatenate the input strings
    combined_string = document_type + section_number_str + task_str
    # Encode the combined string to bytes
    encoded_string = combined_string.encode("utf-8")
    # Create a hash object and generate the hash
    hash_obj = hashlib.sha256(encoded_string)
    # Return the hexadecimal representation of the digest
    return hash_obj.hexdigest()


def remove_text_chunk(original_text, chunk_to_remove):
    """
    Removes a chunk of text from the end of another chunk of text if it exists.

    Args:
        original_text (str): The original chunk of text.
        chunk_to_remove (str): The chunk of text to remove from the end of the original text.

    Returns:
        str: The original text with the specified chunk removed if it was found at the end.
    """
    if original_text.endswith(chunk_to_remove):
        # Calculate the start position of the chunk to remove
        start_pos = len(original_text) - len(chunk_to_remove)
        # Remove the chunk by slicing the original text up to the start position
        return original_text[:start_pos]
    else:
        # Return the original text unchanged if the chunk is not at the end
        return original_text


def dequeue_all_matching(update_queue, match_type, match_value):
    """
    Dequeues all items from the queue that match a given value.

    Args:
        update_queue: The queue to process, expected to be an instance of queue.Queue.
        match_type (str): The type of message to match.
        match_value (bool): The value to match.

    Returns:
        int: The count of dequeued items matching the criteria.
        A new queue object with non-matching items preserved.
    """
    # Temporarily, you can use type hinting for clarity if you wish, but it's not necessary
    temp_queue = type(
        update_queue
    )()  # Instantiate a new queue of the same type as update_queue
    match_count = 0  # Counter for matching items

    while not update_queue.empty():
        try:
            message_type, message_content = update_queue.get_nowait()
            if message_type == match_type and message_content == match_value:
                match_count += 1
            else:
                temp_queue.put((message_type, message_content))
        except Exception as e:  # Catch a broader exception if not importing QueueEmpty
            break

    return match_count, temp_queue


def time_it(func):
    """
    Decorator that measures the execution time of a function.

    Args:
        func (callable): The function to measure.

    Returns:
        callable: The wrapped function with execution time measurement.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time of the function
        result = func(*args, **kwargs)  # Execute the function
        end_time = time.time()  # Record the end time of the function
        time_taken = end_time - start_time  # Calculate the duration
        print(f"Function '{func.__name__}' took {time_taken:.2f} seconds to run.")
        return result

    return wrapper


def add_parser_model(model_name, dataclass):
    """
    Decorator that adds a 'parser_model' attribute to the result of a function.

    Args:
        model_name (str): The name of the parser model to add.
        dataclass: The dataclass to which the 'parser_model' attribute is added.

    Returns:
        callable: The decorated function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Call the original function
            result = func(*args, **kwargs)
            # Assuming the result is an instance of Message, add or modify the parser_model attribute
            if isinstance(result, dataclass):
                # Dynamically add or update the parser_model attribute
                setattr(result, "parser_model", model_name)
            return result

        return wrapper

    return decorator


def read_json_from_file(file_path):
    """
    Reads a JSON object from a file.

    :param file_path: Path to the JSON file.
    :return: The JSON object.
    """
    with open(file_path, "r") as file:
        return json.load(file)


def compare_json_files(file_path1, file_path2):
    """
    Compares two JSON files for equality, considering both structure and values.

    Args:
        file_path1 (str): Path to the first JSON file.
        file_path2 (str): Path to the second JSON file.

    Returns:
        bool: True if the files are equal, False otherwise.
    """

    def compare(data1, data2):
        """
        Recursively compare data structures.

        :param data1: First data structure.
        :param data2: Second data structure.
        :return: True if data structures are equal, False otherwise.
        """
        if type(data1) != type(data2):
            return False

        if isinstance(data1, dict):
            if len(data1) != len(data2):
                return False
            for key in data1:
                if key not in data2:
                    return False
                if not compare(data1[key], data2[key]):
                    return False
            return True
        elif isinstance(data1, list):
            try:
                sorted_data1 = sorted(data1)
                sorted_data2 = sorted(data2)
            except TypeError:
                # If elements of the list are unsortable (e.g., dictionaries), we cannot simply sort them.
                # In this case, you might need a more sophisticated approach or decide to enforce order matters.
                return False
            if len(data1) != len(data2):
                return False
            return all(
                compare(item1, item2)
                for item1, item2 in zip(sorted_data1, sorted_data2)
            )
        else:
            return data1 == data2

    data1 = read_json_from_file(file_path1)
    data2 = read_json_from_file(file_path2)

    return compare(data1, data2)


def detailed_compare_json_files(file_path1, file_path2, path):
    """
    Performs a detailed comparison of two JSON files, reporting differences.

    Args:
        file_path1 (str): Path to the first JSON file.
        file_path2 (str): Path to the second JSON file.
        path (str): The base path for reporting differences.

    Returns:
        None
    """

    def compare_and_report(data1, data2, path):
        """Recursively compare data, reporting differences, including path information."""
        # Handle NoneType comparisons explicitly
        if data1 is None or data2 is None:
            if data1 is None and data2 is not None:
                print(
                    f"Null value in first JSON but found {type(data2).__name__} at path: '{path}'"
                )
            elif data2 is None and data1 is not None:
                print(
                    f"Found {type(data1).__name__} in first JSON but null value in second JSON at path: '{path}'"
                )
            return

        if type(data1) != type(data2):
            print(
                f"Type mismatch at '{path}': {type(data1).__name__} vs {type(data2).__name__}"
            )
            return

        if isinstance(data1, dict):
            for key in set(data1.keys()).union(data2.keys()):
                new_path = (
                    f"{path}.{key}" if path else key
                )  # Construct new path for deeper comparison
                if key in data1 and key not in data2:
                    print(
                        f"Key '{key}' found in first JSON but not in second JSON. Path: '{new_path}'"
                    )
                elif key not in data1 and key in data2:
                    print(
                        f"Key '{key}' found in second JSON but not in first JSON. Path: '{new_path}'"
                    )
                else:
                    compare_and_report(data1[key], data2[key], new_path)
        elif isinstance(data1, list):
            if len(data1) != len(data2):
                print(f"List length mismatch at '{path}': {len(data1)} vs {len(data2)}")
            # Assume lists are to be compared in order; if not, a sorting or other mechanism might be required
            for i, (item1, item2) in enumerate(zip(data1, data2)):
                compare_and_report(item1, item2, f"{path}[{i}]")
        else:
            if data1 != data2:
                print(f"Value mismatch at '{path}': {data1} vs {data2}")

    data1 = read_json_from_file(file_path1)
    data2 = read_json_from_file(file_path2)

    compare_and_report(data1, data2, path)


def change_filename_in_path(original_path, new_filename):
    """
    Changes the filename in a file path to a new filename.

    Args:
        original_path (str): The original file path.
        new_filename (str): The new filename to replace the original filename in the path.

    Returns:
        str: The new file path with the original directory path and the new filename.
    """
    # Split the original path into directory and filename
    directory_path = os.path.dirname(original_path)

    # Join the directory path with the new filename
    new_path = os.path.join(directory_path, new_filename)

    return new_path


def remove_file_extension(filename):
    """
    Removes the file extension from a filename.

    Args:
        filename (str): The filename from which to remove the extension.

    Returns:
        str: The filename without its extension.
    """
    # Split the filename into root and extension
    root, _ = os.path.splitext(filename)

    return root


def get_cache_dir():
    """Returns the cache directory.  Uses the standard XDG conventions of ~/.cache/celi unless XDG_CACHE_HOME is set.

    Ensures that the cache directory is created.
    """
    cache_dir = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    celi_cache_dir = cache_dir / "celi"
    celi_cache_dir.mkdir(parents=True, exist_ok=True)
    return celi_cache_dir
