import json
from itertools import tee, chain, islice

# TODO -> We already have a save json function in utils.utils, deprecate this
def save_to_json(filename, output_folder, toc, toc_content):
    schema_filename = f"{output_folder}/{filename}_schema.json"
    filled_filename = f"{output_folder}/{filename}_filled.json"

    with open(schema_filename, "w") as sf:
        json.dump(toc, sf)

    with open(filled_filename, "w") as ff:
        json.dump(toc_content, ff)

    return schema_filename, filled_filename

def previous_next_helper(some_iterable):
    """
    Given an iterable, return a zip object with the previous item, current item,
    and next item for each item in the iterable

    Parameters
    ----------
    some_iterable : Iterable
        An iterable to iterate through.

    Returns
    -------
    Iterable
        A zip object containing the previous item, current item, and next item for each item in the iterable.
    """
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

def dict_to_list_of_lists(toc_dict):
    """
    Converts a dictionary containing a table of contents (ToC) into a list of lists format.

    Args:
        toc_dict (dict): Dictionary containing the "toc" key with a list of dictionaries,
                         each representing a section with "level", "section_name", and "page_number".

    Returns:
        list of lists: A list where each sublist represents a section and contains
                       [level, section_name, page_number].
    """
    toc_list = []
    for item in toc_dict['toc']:
        toc_list.append([item['section_number'], item['section_name'], item['page_number']])
    return toc_list

def toc_iterator(toc):
    """
    Iterates over ToC to provide previous, current, and next entries.
    """
    prevs, items, nexts = tee(toc, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)


