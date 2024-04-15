"""
This module, utils.codex, provides a suite of utility functions for interacting with MongoDB.
It includes a singleton class that manages connections to the database and offers methods for common database operations,
such as saving documents with versioning, logging messages, and retrieving documents.

The MongoDBUtilitySingleton class within this module acts as a centralized point of access to the database,
ensuring that only one instance of the database connection is created throughout the application's lifecycle.
It automates the management of MongoDB service startup and shutdown, and provides methods for various CRUD operations.

The class is designed to be thread-safe, making it suitable for use in multi-threaded applications.
By utilizing a singleton pattern, it ensures that database operations are consistently executed
without the overhead of creating multiple instances of database connections.

Key Features:
- Singleton pattern for a single MongoDB client instance.
- Automated MongoDB service management on application start/exit.
- Versioning support for document updates to maintain historical data.
- Logging functionality for auditing and debugging purposes.
- Retrieval of active or all versions of a document.
- Methods for adding, updating, and extracting specific data from documents.
"""

import logging
import subprocess
import atexit
import threading
from tracemalloc import start
from httpx import get
from llm_core.llm.base import ChatCompletion
from pymongo import MongoClient
from datetime import datetime

from celi_framework.utils.utils import generate_hash_id

logger = logging.getLogger(__name__)


class MongoDBUtilitySingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(
        cls,
        id_prefix: str = "process",
        db_url: str = "mongodb://localhost:27017/",
        db_name: str = "test_db",
        external_db: bool = False,
    ):
        with cls._lock:
            if cls._instance is None:
                logger.info(f"Creating a new instance of {cls.__name__}")
                cls._instance = super().__new__(cls)
                # Initialize MongoDB client here
                cls._timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                cls._id = {f"{id_prefix}-{cls._timestamp}"}
                cls._instance.db_url = db_url
                cls._instance.client = MongoClient(db_url)
                cls._instance.db = cls._instance.client[db_name]
                if not external_db:
                    cls.start_mongodb()  # Start MongoDB when the instance is first created
                    atexit.register(
                        cls.stop_mongodb
                    )  # Register MongoDB to stop when script exits
            else:
                assert next(
                    iter(cls._instance._id)
                ).startswith(
                    id_prefix
                ), f"ID prefix mismatch: {cls._instance._id} does not start with {id_prefix}"
                assert (
                    cls._instance.db_url == db_url
                ), f"DB URL mismatch: {cls._instance.db_url} does not match {db_url}"
                assert (
                    cls._instance.db.name == db_name
                ), f"DB name mismatch: {cls._instance.db.name} does not match {db_name}"
        return cls._instance

    @staticmethod
    def get_instance():
        """Gets the singleton, assuming it has been created and configured elsewhere."""
        assert (
            MongoDBUtilitySingleton._instance is not None
        ), "Instance has not been created yet"
        return MongoDBUtilitySingleton._instance

    @staticmethod
    def start_mongodb():
        try:
            # Start MongoDB using Homebrew services
            subprocess.run(
                ["brew", "services", "start", "mongodb-community"],
                check=True,
                capture_output=True,
            )
            logger.info("MongoDB started successfully.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Failed to start MongoDB: {e}")

    @staticmethod
    def stop_mongodb():
        try:
            # Stop MongoDB using Homebrew services
            subprocess.run(
                ["brew", "services", "stop", "mongodb-community"],
                check=True,
                capture_output=True,
            )
            logger.info("MongoDB stopped successfully.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Failed to stop MongoDB: {e}")

    def update_timestamp(self, new_timestamp):
        """Updates the timestamp used for logging and document versioning."""
        self._timestamp = new_timestamp

    def save_document_with_versioning(self, document, collection_name):
        try:
            """Saves or updates a document with versioning."""
            query = {"id": document["id"]}
            latest_version = self.db[collection_name].find_one(
                query, sort=[("version", -1)]
            )

            new_version = 1
            if latest_version:
                # Increment version for new document
                new_version = latest_version["version"] + 1
                # Mark the latest version as a shadow document
                self.db[collection_name].update_one(
                    {"_id": latest_version["_id"]}, {"$set": {"is_shadow": True}}
                )

            document["version"] = new_version
            # document['timestamp'] = self._timestamp
            document["is_shadow"] = False  # Active document
            self.db[collection_name].insert_one(document)
        except Exception as e:
            # Log the error and handle it appropriately
            logger.exception(f"Error saving document with versioning: {e}")
            return None  # Or raise a custom exception

    def log_message(self, message, level, collection_name="logs"):
        """Logs a message to MongoDB."""
        log_entry = {
            "message": message,
            "level": level,
            # 'timestamp': self._timestamp
            "timestamp": self._timestamp,
        }
        try:
            self.db[collection_name].insert_one(log_entry)
        except Exception as e:
            logger.exception(f"Error saving log to MongoDB: {e}")

    def print_all_saved_logs(self):
        """Fetches and prints all saved logs from MongoDB."""
        logs = (
            self.db["logs"].find().sort("timestamp")
        )  # , -1)  # Assuming 'logs' is your collection name
        for log in logs:
            print(
                f"Timestamp: {log['timestamp']} | Level: {log['level']} | Message: {log['message']}"
            )

    def get_active_document(self, doc_id, collection_name):
        """Retrieves the latest active version of a document."""
        return self.db[collection_name].find_one({"id": doc_id, "is_shadow": False})

    def get_document_versions(self, doc_id, collection_name):
        """Retrieves all versions of a document."""
        return list(self.db[collection_name].find({"id": doc_id}).sort("version", 1))

    def get_document_by_id(self, document_id, collection_name):
        """
        Fetches a document by its ID from the specified collection.

        Args:
            document_id (str): The ID of the document to fetch.
            collection_name (str): The name of the collection where the document is stored.

        Returns:
            dict: The fetched document or None if not found.
        """
        return self.db[collection_name].find_one({"_id": document_id})

    def extract_prompt_completion_attributes(self, document):
        """
        Extracts attributes from a document representing a prompt completion.

        Args:
            document (dict): The document from which to extract prompt completion attributes.

        Returns:
            dict: A dictionary of extracted attributes.
        """
        if document is None:
            return None

        attributes = {
            "system_message": document.get("system_message", ""),
            "user_message": document.get("user_message", ""),
            "prompt_completion": document.get("prompt_completion", ""),
            "timestamp": document.get("timestamp", ""),
            "template_id": document.get("template_id", ""),
        }
        return attributes

    def extract_function_return_attributes(self, document):
        """
        Extracts attributes from a document representing a function return.

        Args:
            document (dict): The document from which to extract function return attributes.

        Returns:
            dict: A dictionary of extracted attributes.
        """
        if document is None:
            return None

        attributes = {
            "function_name": document.get("function_name", ""),
            "arguments": document.get("arguments", {}),
            "function_return": document.get("function_return", ""),
            "timestamp": document.get("timestamp", ""),
            "template_id": document.get("template_id", ""),
        }
        return attributes

    def add_or_update_fields_in_document(
        self, collection_name, document_id, new_fields
    ):
        """
        Adds or updates fields in a document within a specified collection.

        Args:
            collection_name (str): The name of the collection.
            document_id (str): The unique identifier of the document to update.
            new_fields (dict): A dictionary containing the new field(s) and value(s) to be added or updated in the document.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            result = self.db[collection_name].update_one(
                {"_id": document_id}, {"$set": new_fields}
            )
            if result.modified_count > 0:
                logger.info(
                    f"Document with ID {document_id} in collection '{collection_name}' successfully updated."
                )
                return True
            else:
                logger.info(
                    f"No changes made to the document with ID {document_id} in collection '{collection_name}'. It might already contain the updates or does not exist."
                )
                return False
        except Exception as e:
            logger.info(
                f"Failed to update document with ID {document_id} in collection '{collection_name}': {e}"
            )
            return False

    def check_llm_cache(self, **kwargs):
        id = generate_hash_id(kwargs)
        ret = self.get_document_by_id(id, "llm_cache")
        return ret

    def cache_llm_response(self, response: dict, **kwargs):
        id = generate_hash_id(kwargs)
        document = {"_id": id, **response}
        self.db["llm_cache"].insert_one(document)
