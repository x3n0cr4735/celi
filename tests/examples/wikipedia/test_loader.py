"""
This module conducts a suite of automated tests to ensure the effectiveness of Wikipedia content retrieval and processing
within the CELI framework. It is designed to verify the robustness of components responsible for fetching Wikipedia
content, indexing with references, chunking text for efficient indexing, and creating nodes from references. While the
module focuses on generic functionalities, it's currently hardcoded to specific examples, illustrating the framework's
capabilities across diverse topics.

By utilizing classes such as `ReferenceLoader` for parsing referenced content and `VectorStoreIndex` for indexing, the
module demonstrates the framework's ability to manage and analyze large-scale data sources. Integration with MongoDB
for persistent storage showcases advanced data management capabilities within the CELI ecosystem.

Key Functions (Note: Functions are currently hardcoded to specific examples for testing):
- `test_get_wikipedia_index`: Tests retrieving and caching an index from a Wikipedia page, verifying the ability to
  access and read cached indexes.
- `test_get_wikipedia_index_faster`: Validates the faster retrieval of Wikipedia indexes without including content
  references, employing efficient caching methods.
- `test_load_content_from_wikipedia_url`: Verifies direct content and reference loading from Wikipedia URLs, asserting
  the presence of specific section headers.
- `test_load_drug_content_from_wikipedia_url`: Focuses on loading content from pharmaceutical-related Wikipedia pages,
  testing for detailed information in key medical sections.
- `test_load_content_from_wikipedia_url_hard`: Addresses content loading from Wikipedia pages known for parsing
  difficulties, ensuring accurate schema extraction and content parsing.
- `test_load_reference`: Tests the parsing and loading of document metadata from Wikipedia content references, ensuring
  accurate representation.
- `test_create_nodes_from_references`: Validates the creation of content nodes from Wikipedia references, ensuring
  correct text and metadata representation.
- `test_content_chunking`: Examines text chunking for indexing Wikipedia content, focusing on handling long sections
  efficiently.
- `test_content_chunking_long`: Tests chunking mechanisms for lengthy content from specified URLs, ensuring proper
  indexing and node creation.

While the current tests are designed around hardcoded examples, they underscore the CELI framework's comprehensive
approach to content retrieval and processing. Future enhancements aim to generalize these tests, moving away from
hardcoded examples towards more dynamically generated test scenarios.
"""

import logging
import os

import pytest
from celi_framework.examples.wikipedia.Index_cache import (
    ChromaDBIndexCache,
    IndexFileCache,
)
from celi_framework.examples.wikipedia.index import (
    ReferenceLoader,
    get_wikipedia_index,
    index_wikipedia_url_with_references,
)
from celi_framework.examples.wikipedia.loader import (
    ContentReference,
    load_content_from_wikipedia_url,
)
from celi_framework.utils.utils import get_cache_dir
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.schema import NodeRelationship

logger = logging.getLogger(__name__)


@pytest.mark.skip(reason="Uses LLM")
def test_get_wikipedia_index():
    index = get_wikipedia_index(
        "https://en.wikipedia.org/wiki/Led_Zeppelin",
        cache_type=IndexFileCache,
        ignore_updates=True,
    )

    # Test that we can reload from cache and read all the documents
    cache_loc = os.path.join(get_cache_dir(), "index/CR-1876773ababf33b8")
    storage_context = StorageContext.from_defaults(persist_dir=cache_loc)

    # Reload index to make sure we can read it.
    index = load_index_from_storage(storage_context)
    hashes = index.docstore.get_all_document_hashes()
    for hash, doc_id in hashes.items():
        index.docstore.get_document(doc_id)


@pytest.mark.skip(reason="Uses LLM")
def test_get_wikipedia_index_faster():
    index = get_wikipedia_index(
        "https://en.wikipedia.org/wiki/Led_Zeppelin",
        include_references=False,
        cache_type=ChromaDBIndexCache,
        ignore_updates=True,
    )
    ret = index.as_query_engine().query("When was the first album released?")
    assert "1969" in ret.response


def test_load_content_from_wikipedia_url():
    content, references = load_content_from_wikipedia_url(
        "https://en.wikipedia.org/wiki/Led_Zeppelin"
    )
    section_headers = [_.title for _ in content]
    assert len(references) > 50
    assert "History" in section_headers
    assert "Discography" in section_headers
    history = [_ for _ in content if _.title == "History"][0]
    assert len(history.children) >= 6
    assert len(history.children[0].references) >= 3
    assert "London-based session guitarist" in history.children[0].content


def test_load_drug_content_from_wikipedia_url():
    content, references = load_content_from_wikipedia_url(
        "https://en.wikipedia.org/wiki/Sirolimus"
    )
    section_headers = [_.title for _ in content]
    assert len(references) > 80
    assert "Medical uses" in section_headers
    assert "Chemistry" in section_headers
    child = [_ for _ in content if _.title == "Medical uses"][0]
    assert len(child.children) >= 5
    assert len(child.references) >= 3
    assert "organ transplant rejection" in child.content


@pytest.mark.skip(reason="Uses LLM")
def test_load_content_from_wikipedia_url_hard():
    # Semaglutide failed on first parsing
    content, references = load_content_from_wikipedia_url(
        "https://en.wikipedia.org/wiki/Semaglutide"
    )
    section_headers = [_.title for _ in content]
    assert len(references) > 50
    assert "History" in section_headers
    index = get_wikipedia_index(
        "https://en.wikipedia.org/wiki/Semaglutide",
        include_references=True,
        cache_type=ChromaDBIndexCache,
        ignore_updates=True,
    )
    all_metas = index.vector_store._collection.get(include=["metadatas"])["metadatas"]
    schema = {
        _["celi_section_number"]: _["title"]
        for _ in all_metas
        if "celi_section_number" in _
    }
    assert "History" in schema.values()


def test_load_reference():
    ref = ContentReference(
        number="7",
        title='"Together Biography, Songs, & Albums"',
        href="cite_note-8",
        url="https://www.allmusic.com/artist/together-mn0000520166/biography",
    )
    ref_loader = ReferenceLoader()
    source_url = "https://en.wikipedia.org/wiki/Led_Zeppelin"
    doc = ref_loader.create_doc_from_reference(source_url, ref)
    logger.info(doc)
    logger.info(doc.metadata)
    assert doc.metadata["celi_role"] == "reference"
    assert doc.metadata["celi_reference_source"] == source_url
    assert doc.metadata["URL"] == ref.url
    assert "AllMusic" in doc.text


def test_create_nodes_from_references():
    refs = [
        ContentReference(
            number="7",
            title='"Together Biography, Songs, & Albums"',
            href="cite_note-8",
            url="https://www.allmusic.com/artist/together-mn0000520166/biography",
        )
    ]
    ref_loader = ReferenceLoader()
    nodes = ref_loader.create_nodes_from_references(
        "https://en.wikipedia.org/wiki/Led_Zeppelin", refs
    )
    print(nodes)
    assert len(nodes) == 1
    assert "AllMusic" in nodes[0].text
    assert nodes[0].metadata["URL"] == refs[0].url


@pytest.mark.skip(reason="Uses LLM")
def test_content_chunking():
    index = index_wikipedia_url_with_references(
        "https://en.wikipedia.org/wiki/Queen_(band)", include_references=False
    )
    docs = index.docstore.docs
    # Extra nodes are created when the text for a section is too long.
    extra_nodes = [
        _ for _ in docs.values() if _.metadata.get("celi_main_chunk") == False
    ]
    assert len(extra_nodes) > 0
    logger.info(f"Extra nodes: {len(extra_nodes)}")
    ex = extra_nodes[0]
    parent = docs[ex.relationships[NodeRelationship.PARENT].node_id]
    assert ex.metadata["celi_section_number"] == parent.metadata["celi_section_number"]
    assert parent.metadata["celi_main_chunk"] == True
    assert ex.relationships[NodeRelationship.PREVIOUS].node_id == parent.node_id
    assert parent.relationships[NodeRelationship.NEXT].node_id == ex.node_id


#
