"""Creates LlamaIndex indices from Wikipedia documents.

Each Wikipedia page becomes a single LlamaIndex Document.
Each reference link from the wikipedia page becomes a LlamaIndex document that is broken into nodes with a standard splitter.

The different content sections in that page are each turned into a node.
Each node has the following relationships:
* References: A link to a Document from the references.
* Previous: Previous node in the content.
* Next: Next node in the content.
* Parent: The parent node in the content hierarchy.
* Children: The child nodes in the content hierarchy.

It has has the following metadata:
* Level: Integer representing the depth of the node in the content hierarchy.  1 is a root node.
* Title: The title of the node.
* href: The page anchor for this node.  This uniquely identifies the node on the page.
* URL: The URL of the wikipedia page.
"""

from __future__ import annotations
from functools import lru_cache
import logging
from typing import Iterable, List, Optional, Type
from llama_index.core.node_parser.text import SentenceSplitter
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.schema import TextNode, NodeRelationship
from llama_index_client import RelatedNodeInfo
from requests import Request
import requests
from llama_index.core import StorageContext
from celi_framework.examples.wikipedia.Index_cache import ChromaDBIndexCache, IndexCache
from celi_framework.examples.wikipedia.caching_beautiful_soup_reader import (
    CachingBeautifulSoupWebReader,
)
from celi_framework.examples.wikipedia.loader import (
    ContentHierarchyNode,
    ContentReference,
    load_content_from_wikipedia_url,
)
from celi_framework.examples.wikipedia.wikipedia_utils import get_cached_session
from celi_framework.utils.token_counters import token_counter_og

logger = logging.getLogger(__name__)


@lru_cache(maxsize=50)
def get_wikipedia_index(
    url: str,
    include_references: bool = True,
    include_content: bool = True,
    cache_type: Type[IndexCache] = ChromaDBIndexCache,
    ignore_updates: bool = False,
):
    """This is the top-level function to get an index for a wikipedia page.

    Returns a cached version of the index if it is up to date.  Otherwise, ceates it by reading the page, breaking it down into it's content hierarchy, getting all references, and then embedding them.

    For caching, we use the requests_cache.  If the cached page is still valid and the vector index is more recent than the cache entry, we use the cache.
    """

    cache_key, content_cached_at = get_cached_key_and_last_content_update(
        url, ignore_updates
    )

    prefix = f"{'C' if include_content else ''}{'R' if include_references else ''}-"

    index_cache = cache_type(f"{prefix}{cache_key}")
    index_cache_created_at = index_cache.get_created_at()
    if (
        content_cached_at
        and index_cache_created_at
        and (index_cache_created_at > content_cached_at or ignore_updates)
    ):
        logger.info(f"Using cached index {index_cache.name} for {url}.")
        storage_context = index_cache.get_storage_context()
        index = index_cache.get_index()
    else:
        logger.info(
            f"Building a new index for {url} named {index_cache.name}.  Last index creation date: {index_cache_created_at} Last content date: {content_cached_at}"
        )
        storage_context = index_cache.get_storage_context()
        index_cache.remove_storage()
        index = index_wikipedia_url_with_references(
            url,
            storage_context=storage_context,
            include_content=include_content,
            include_references=include_references,
        )
        index_cache.persist()
    return index


def index_wikipedia_url_with_references(
    url: str,
    storage_context: Optional[StorageContext] = None,
    include_references: bool = True,
    include_content: bool = True,
):
    """Creates a LlamaIndex Vector Index from the content of a wikipedia page and all its references."""
    logger.info(f"Loading content for {url}.")
    toc, references = load_content_from_wikipedia_url(
        url, include_references=include_references
    )

    logger.info(f"Retrieving references for {url}.")
    reference_nodes = ReferenceLoader().create_nodes_from_references(url, references)

    logger.info(f"Indexing content for {url}.")
    content_nodes = (
        create_node_hierarchy(url, toc, reference_nodes) if include_content else []
    )

    all_nodes = content_nodes + reference_nodes
    max_len = 0
    longest_node = None
    for node in all_nodes:
        if len(node.text) >= max_len:
            max_len = token_counter_og(node.text)
            longest_node = node
    logger.info(
        f"{len(all_nodes)} nodes. Longest node is {max_len} tokens: {longest_node.metadata}."
    )
    index = VectorStoreIndex(nodes=all_nodes, storage_context=storage_context)
    logger.info(f"Finished created index for {url}.")
    return index


def create_node_hierarchy(
    source_url: str, toc: List[ContentHierarchyNode], references: List[TextNode]
):
    """Creates LlamaIndex nodes from a wikipedia page and its references.

    Args:
        source_url: The URL of the wikipedia page.
        toc: The table of contents of the wikipedia page.
        references: The references of the wikipedia page.

    Returns:
        Document: The LlamaIndex Document representing the wikipedia page.
    """

    reference_map = {}
    for ref in references:
        rl = reference_map.get(ref.metadata["celi_reference_href"], [])
        rl.append(ref)
        reference_map[ref.metadata["celi_reference_href"]] = rl

    standard_metadata = {"URL": source_url}
    all_nodes = []
    splitter = SentenceSplitter()
    EXCLUDED_KEYS = [
        "celi_href",
        "celi_references_node_ids",
        "celi_main_chunk",
        "celi_chunk_index",
        "URL",
    ]

    def recurse_node(
        current: ContentHierarchyNode,
        parent: Optional[TextNode] = None,
        prev: Optional[TextNode] = None,
        level: int = 1,
    ):
        section_metadata = {
            **standard_metadata,
            "title": current.title,
            "celi_href": current.href,
            "celi_section_number": current.number if current.number else "0",
            "celi_section_level": level,
            # Store references as metadata because we can't define custom NodeRelationship types
            "celi_references_node_ids": ",".join(
                node.node_id
                for ref in current.references
                if ref.href in reference_map
                for node in reference_map[ref.href]
            ),
        }
        chunks = splitter.split_text(current.content)  # type: ignore
        # Create the main node for the first chunk.  Additional chunks will be added as children.
        node = TextNode(
            text=chunks[0],
            metadata={
                **section_metadata,
                "celi_main_chunk": True,
                "celi_chunk_index": 0,
            },
            excluded_embed_metadata_keys=EXCLUDED_KEYS,
            excluded_llm_metadata_keys=EXCLUDED_KEYS,
        )

        def add_relationship(
            source: TextNode, relationship: NodeRelationship, target: TextNode
        ):
            source.relationships[relationship] = RelatedNodeInfo(
                node_id=target.node_id, metadata={}
            )

        def add_child_relationship(parent: TextNode, child: TextNode):
            parent.relationships[NodeRelationship.CHILD].append(
                RelatedNodeInfo(node_id=child.node_id, metadata={})
            )

        if parent:
            add_relationship(node, NodeRelationship.PARENT, parent)
            add_child_relationship(parent, node)
        if prev:
            add_relationship(node, NodeRelationship.PREVIOUS, prev)
            add_relationship(prev, NodeRelationship.NEXT, node)

        if current.children or len(chunks) > 1:
            node.relationships[NodeRelationship.CHILD] = []
        all_nodes.append(node)

        prev = node
        for ix, chunk in enumerate(chunks[1:]):
            # logger.debug("Processing extra chunk")
            extra_node = TextNode(
                text=chunk,
                metadata={
                    **section_metadata,
                    "celi_main_chunk": False,
                    "celi_chunk_index": ix + 1,
                },
                excluded_embed_metadata_keys=EXCLUDED_KEYS,
                excluded_llm_metadata_keys=EXCLUDED_KEYS,
            )
            add_relationship(extra_node, NodeRelationship.PARENT, node)
            add_child_relationship(node, extra_node)
            add_relationship(extra_node, NodeRelationship.PREVIOUS, prev)
            add_relationship(prev, NodeRelationship.NEXT, extra_node)
            all_nodes.append(extra_node)
            prev = extra_node

        for child in current.children:
            prev = recurse_node(child, parent=node, prev=prev, level=level + 1)
        return prev

    prev = None
    for root in toc:
        prev = recurse_node(root, parent=None, prev=prev, level=1)

    return all_nodes


class ReferenceLoader:
    def __init__(self, allowed_failure_rate=0.5):
        self.loader = CachingBeautifulSoupWebReader()
        self.session = get_cached_session()
        self.allowed_failure_rate = allowed_failure_rate

    def create_nodes_from_references(
        self, source_url: str, references: Iterable[ContentReference]
    ):
        splitter = SentenceSplitter(include_metadata=True, include_prev_next_rel=True)

        docs = self.create_docs_from_references(source_url, references)
        all_nodes = []
        for doc in docs:
            text = doc.get_content()
            chunks = splitter.split_text(text)
            MAX_CHUNKS = 20
            nodes = [
                TextNode(
                    text=chunk,
                    metadata={
                        **doc.metadata,
                        "celi_chunk_index": ix,
                    },
                    excluded_embed_metadata_keys=[
                        "celi_reference_href",
                        "celi_reference_source",
                        "celi_chunk_index",
                    ],
                    excluded_llm_metadata_keys=[
                        "celi_reference_href",
                        "celi_reference_source",
                        "celi_chunk_index",
                    ],
                )
                for ix, chunk in enumerate(chunks)
                if ix < MAX_CHUNKS
            ]
            if len(chunks) > MAX_CHUNKS:
                logger.warning(
                    f"Reference {doc.metadata['celi_reference_name']} has more than {MAX_CHUNKS} chunks.  Only taking the first {MAX_CHUNKS}."
                )
            all_nodes.extend(nodes)
        return all_nodes

    def create_docs_from_references(
        self, source_url: str, references: List[ContentReference]
    ) -> List[TextNode]:
        ret = []
        for reference in references:
            try:
                d = self.create_doc_from_reference(source_url, reference)
                ret.append(d)
            except Exception as e:
                logger.exception(f"Skipping reference {reference} due to error: {e}")
        if (
            len(references) > 0
            and len(ret) / len(references) < self.allowed_failure_rate
        ):
            raise ValueError(
                f"Too many failures loading references ({len(ret)} out of {len(references)}) .  Aborting."
            )
        return ret

    def create_doc_from_reference(self, source_url: str, reference: ContentReference):
        doc = self.loader.load_data([reference.url], session=self.session)[0]
        doc.metadata["celi_role"] = "reference"
        doc.metadata["celi_reference_number"] = reference.number
        doc.metadata["celi_reference_name"] = reference.title
        doc.metadata["celi_reference_href"] = reference.href
        doc.metadata["celi_reference_source"] = source_url
        return doc


def get_cached_key_and_last_content_update(url, ignore_updates: bool = False):
    cache = get_cached_session().cache
    cache_key = cache.create_key(Request("GET", url))
    cache_entry = cache.get_response(cache_key)
    if not cache_entry:
        cache_entry_is_valid = False
    elif ignore_updates:
        cache_entry_is_valid = True
        logger.debug(
            f"Ignore updates is set to True.  Using existing cache entry for {url}."
        )
    elif cache_entry.is_expired:
        etag = cache_entry.headers.get("ETag")
        last_modified = cache_entry.headers.get("last-modified")
        headers = (
            {"If-None-Match": etag} if etag else {"If-Modified-Since": last_modified}
        )
        try:
            response = requests.head(url, headers=headers)
            cache_entry_is_valid = response.status_code == 304
            if cache_entry_is_valid:
                logger.debug(f"Cache expired but content hasn't changed for {url}")
            else:
                logger.debug(
                    f"Existing cache is no longer valid for {url}.  Last modified at {response.headers.get('last-modified')}"
                )
        except ConnectionError:
            cache_entry_is_valid = True
            logger.debug(
                f"Can't determine cache validity due to a connection error.  Assuming cache is valid for {url}"
            )
    else:
        cache_entry_is_valid = True
        logger.debug(f"Cache entry still valid for {url}.")
    content_cached_at = cache_entry.created_at if cache_entry_is_valid else None
    return cache_key, content_cached_at
