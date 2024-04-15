"""
This module comprises a suite of test functions aimed at validating the functionality of tools used for interacting with
and extracting information from Wikipedia pages. The suite includes tests for the retrieval of Wikipedia indexes, extraction
of schemas from Wikipedia content, querying Wikipedia entities through structured questions, and mapping references across
diverse Wikipedia entries. Although the tests are built around specific examples, they are intended to demonstrate the
general capabilities of the CELI framework's components in processing and analyzing Wikipedia content.

Key functionalities include leveraging the `WikipediaToolImplementations` class for querying Wikipedia content and
processing retrieved data. This encompasses fetching tables of contents, asking questions about Wikipedia entities,
obtaining text from specified sections, and correlating references between different entries. The module also showcases
the initialization and use of MongoDB utilities for persistent data management within the CELI framework.

Key Functions (Note: Functions currently utilize specific examples for testing purposes):
- `_get_example_index()`: Retrieves a Wikipedia index for a given URL with updates ignored.
- `_get_target_index()`: Retrieves a Wikipedia index for another URL without content.
- `_get_test_tool_impls()`: Creates tool implementations for interacting with Wikipedia pages.
- `test_extract_schema()`: Validates the extraction of a schema from the Wikipedia index.
- `test_ask_question()`: Verifies the ability of the tool to pose and answer questions about the content.
- `test_get_example_references()`: Checks the retrieval of references for specific sections within an example index.
- `test_get_text_for_section()`: Confirms fetching the text for specified sections of content.
- `test_corresponding_target_references()`: Examines the identification of corresponding references between two indexes.

The module's tests are crucial for ensuring the proper functioning of data retrieval and processing components of
the framework, facilitating the dependable use of Wikipedia data for a range of applications within the CELI ecosystem.
"""

import logging
import os

from dotenv import load_dotenv
from celi_framework.examples.wikipedia.index import get_wikipedia_index
from celi_framework.examples.wikipedia.tools import WikipediaToolImplementations
from celi_framework.utils.codex import MongoDBUtilitySingleton
from celi_framework.utils.utils import str2bool

load_dotenv()
logger = logging.getLogger(__name__)


def _get_example_index():
    return get_wikipedia_index(
        "https://en.wikipedia.org/wiki/Led_Zeppelin", ignore_updates=True
    )


def _get_target_index():
    return get_wikipedia_index(
        "https://en.wikipedia.org/wiki/Jonas_Brothers",
        include_content=False,
        ignore_updates=True,
    )


def _get_test_tool_impls():
    return WikipediaToolImplementations(
        "https://en.wikipedia.org/wiki/Led_Zeppelin",
        "https://en.wikipedia.org/wiki/Jonas_Brothers",
        ignore_updates=True,
    )


def test_extract_schema():
    index = _get_example_index()
    toc = WikipediaToolImplementations._extract_schema(index)
    logger.info(f"TOC {toc}")
    assert toc["1"] == "History"
    assert toc["2"] == "Musical style"


def test_ask_question():
    load_dotenv()
    MongoDBUtilitySingleton(
        db_url=os.environ.get("DB_URL", "mongodb://localhost:27017/"),
        db_name="celi",
        external_db=str2bool(os.environ.get("EXTERNAL_DB", "False")),
    )
    tools = _get_test_tool_impls()
    ret = tools.ask_question_about_target("Who were the three brothers?")
    logger.info(f"Answer: {ret.metadata} {ret.source_nodes}")
    assert "Kevin" in ret.response


def test_get_example_references():
    tools = _get_test_tool_impls()
    ret = tools._get_references_for_example_sections(["1.1"])
    logger.info(f"References: {ret}")
    assert len(ret) > 10


def test_get_text_for_section():
    tools = _get_test_tool_impls()
    ret = tools.get_text_for_sections('{"Example Document": ["1.1"]}')
    assert "Page soon switched from bass to lead guitar" in ret


def test_corresponding_target_references():
    tools = _get_test_tool_impls()
    # Get a few refernce ids
    d = tools.example_index.vector_store._collection.peek()
    ids = [
        id
        for id, metadata in zip(d["ids"], d["metadatas"])
        if "celi_reference_name" in metadata
    ][:3]
    ret = tools._get_corresponding_target_references(ids)
    # logger.info(ret)
