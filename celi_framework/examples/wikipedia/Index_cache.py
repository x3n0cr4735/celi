from abc import ABC, abstractmethod
import logging
from time import sleep
from typing import Any

import chromadb
import datetime
import os
import shutil
from llama_index.core.indices import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.indices.base import BaseIndex

from llama_index.core import StorageContext, load_index_from_storage

from celi_framework.utils.utils import get_cache_dir

logger = logging.getLogger(__name__)


class IndexCache(ABC):
    @abstractmethod
    def get_storage_context(self) -> StorageContext:
        pass

    @abstractmethod
    def get_index(self) -> BaseIndex[Any]:
        pass

    @abstractmethod
    def get_created_at(self) -> datetime.datetime:
        pass

    @abstractmethod
    def remove_storage(self) -> None:
        pass

    @abstractmethod
    def persist(self) -> None:
        pass


class IndexFileCache(IndexCache):
    def __init__(self, name):
        self.name = name
        self.cache_loc = os.path.join(get_cache_dir(), f"index/{self.name}")
        self.cache_loc_exists = os.path.exists(self.cache_loc)
        self.cache_loc_created_date = (
            datetime.datetime.fromtimestamp(
                os.path.getctime(self.cache_loc), tz=datetime.timezone.utc
            )
            if self.cache_loc_exists
            else None
        )

    def get_storage_context(self):
        if self.cache_loc_exists:
            self.storage_context = StorageContext.from_defaults(
                persist_dir=self.cache_loc
            )
        else:
            self.storage_context = StorageContext.from_defaults()
        return self.storage_context

    def get_index(self):
        return load_index_from_storage(self.storage_context)

    def get_created_at(self):
        return self.cache_loc_created_date

    def remove_storage(self):
        if self.cache_loc_exists:
            # Delete the old cache if it exists.  This will reset the creation date and also make sure the new cache data is clean.
            shutil.rmtree(self.cache_loc)

    def persist(self):
        self.storage_context.persist(persist_dir=self.cache_loc)


class ChromaDBIndexCache(IndexCache):
    def __init__(self, name):
        self.name = name
        self.cache_loc = os.path.join(get_cache_dir(), f"index/chroma_db/{self.name}")
        self.cache_loc_exists = os.path.exists(self.cache_loc)
        self.cache_loc_created_date = (
            datetime.datetime.fromtimestamp(
                os.path.getctime(self.cache_loc), tz=datetime.timezone.utc
            )
            if self.cache_loc_exists
            else None
        )
        logger.debug(
            f"ChromaDB index for {self.name} is at {self.cache_loc}, created at {self.cache_loc_created_date}"
        )
        db = chromadb.PersistentClient(path=self.cache_loc)
        chroma_collection = db.get_or_create_collection("celi")
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )

    def get_storage_context(self):
        return self.storage_context

    def get_index(self):
        return VectorStoreIndex.from_vector_store(self.vector_store)

    def get_created_at(self):
        return self.cache_loc_created_date

    def remove_storage(self):
        if self.cache_loc_exists:
            # Delete the old cache if it exists.  This will reset the creation date and also make sure the new cache data is clean.
            shutil.rmtree(self.cache_loc)
            # Sleep for a bit to make sure the directory is deleted.  See this: https://github.com/langchain-ai/langchain/issues/14872
            # Couldn't downgrade chromadb because of llama-index dependencies.
            sleep(1)
            count = 0
            while os.path.exists(self.cache_loc) and count < 3:
                sleep(1)

    def persist(self):
        self.storage_context.persist(persist_dir=self.cache_loc)


# Chroma cache was simpler, so I'm removing the OpenSearch cache for now.
#
# OpenSearch requires these lines in pyproject.toml:
# llama-index-readers-elasticsearch = "^0.1.3"
# llama-index-vector-stores-opensearch = "^0.1.8"
# llama-index-embeddings-ollama = "^0.1.2"
#
# import asyncio
# from llama_index.vector_stores.opensearch import (
#     OpensearchVectorStore,
#     OpensearchVectorClient,
# )
# class OpenSearchIndexCache(IndexCache):
#     def __init__(self, name):
#         self.name = name
#         endpoint = os.environ["OPENSEARCH_ENDPOINT"]  # "http:://localhost:9200"
#         # OpensearchVectorClient stores text in this field by default
#         text_field = "content"
#         # OpensearchVectorClient stores embeddings in this field by default
#         embedding_field = "embedding"
#         # OpensearchVectorClient encapsulates logic for a
#         # single opensearch index with vector search enabled
#         self.client = OpensearchVectorClient(
#             endpoint,
#             self.name.lower(),
#             1536,
#             embedding_field=embedding_field,
#             text_field=text_field,
#         )
#         self.vector_store = OpensearchVectorStore(self.client)
#         self.storage_context = StorageContext.from_defaults(
#             vector_store=self.vector_store
#         )

#     def get_storage_context(self):
#         logger.info(f"Using OpenSearch index {self.name}.")
#         return self.storage_context

#     def get_index(self):
#         logger.info(f"Using OpenSearch index {self.name}.")
#         return VectorStoreIndex.from_vector_store(self.vector_store)

#     def get_created_at(self):
#         exists = asyncio.get_event_loop().run_until_complete(
#             self.client._os_client.indices.exists(index=self.name.lower())
#         )

#         # HACK - we always assume the opensearch index is up to date.
#         return datetime.datetime.now(tz=datetime.timezone.utc) if exists else None

#     def remove_storage(self):
#         pass

#     def persist(self):
#         self.storage_context.persist()
