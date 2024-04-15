"""
The `utils.sql_utils` module offers a set of tools designed for efficient database management, focusing on SQLite for local data storage and offering capabilities for integrating data from MongoDB. This module is essential for applications that require lightweight, disk-based database solutions without the need for a full-fledged DBMS. It is particularly useful for data persistence, analysis, and reporting in Python-based applications.

Features:
- `ManageDB`: A class that encapsulates database management tasks such as creating connections, executing SQL commands, and managing tables within SQLite. It ensures smooth operation through methods tailored for different database operations, including schema checks, table existence verification, and data insertion with conflict handling.
- Data Synchronization: Provides functionality to synchronize data from MongoDB collections to SQLite tables, enabling hybrid database solutions that leverage both document-oriented and relational database models.
- Schema Validation: Ensures that tables within the SQLite database match expected schemas, facilitating data integrity and consistency checks.
- CSV Export: Includes a method for exporting SQLite table data to CSV files using pandas, making it easy to share data or perform further analysis in external tools.
- Decorators for Enhanced Functionality: Incorporates decorators for token counting and timing, which can be applied to database operations to monitor performance and manage resource usage efficiently.

Usage:
This module is intended for developers needing to manage SQLite databases within their Python applications, especially when working with data originating from MongoDB or requiring export to CSV for analysis. It abstracts away the complexities of SQL commands and database connection management, allowing developers to focus on application logic and data processing.

Notes:
Ensure that the SQLite database file path (DB_DIR) is correctly configured in your application settings.
When synchronizing data from MongoDB, ensure that MongoDB is accessible and that the MongoDBUtilitySingleton is properly configured with the correct database URL and name.

TODO: Change so that sqlite db goes in data/project_data/[project_name]/databases

"""

import sqlite3
from typing import List, Dict, Any
from celi_framework.utils.codex import (
    MongoDBUtilitySingleton,
)  # Ensure this import works with your project structure
import pandas as pd
import os


class ManageDB:
    """
    A class to manage database operations with SQLite and to synchronize data from MongoDB.

    Attributes:
        db_name (str): The name of the SQLite database file.
        conn (sqlite3.Connection): The SQLite connection object.
        cursor (sqlite3.Cursor): The cursor object for executing SQL commands in SQLite.
    """

    def __init__(self, db_name: str = "test_evaluations.db"):
        """
        Initializes the ManageDB instance, setting up a connection to an SQLite database.

        Parameters:
            db_name (str): The name of the SQLite database file. Defaults to 'my_database.db'.
        """
        self.db_name = os.path.join(DB_DIR, db_name)

        # Establishes a connection to the specified SQLite database. Creates the database file if it does not exist.
        self.conn = sqlite3.connect(self.db_name)
        # Creates a cursor object to execute SQL commands.
        self.cursor = self.conn.cursor()

    def execute_sql(self, sql: str, params: tuple = (), db_name: str = None):
        """
        Executes a given SQL command with optional parameters on the specified database.

        :param sql (str): SQL command to execute.
        :param params (tuple): Optional parameters for the SQL command.
        :param db_name (str): Name of the database file to execute the SQL command on. Defaults to the instance's default database.
        """

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

    def table_schema_matches(self, table_name: str, schema: Dict[str, str]):
        """
        Checks if the existing table's schema matches the expected schema.
        This method only checks if all expected columns exist, not their data types or constraints.

        :param table_name (str): Name of the table to check.
        :param schema (Dict): Expected schema as a dictionary of column names and types.
        :return: True if the table exists with all expected columns, False otherwise.
        """
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {
            row[1]: row[2] for row in self.cursor.fetchall()
        }  # Column name: Data type

        expected_columns = set(schema.keys())
        actual_columns = set(existing_columns.keys())

        return (
            expected_columns <= actual_columns
        )  # Check if expected columns are a subset of actual columns

    def create_table(self, table_name: str, schema: Dict[str, str]):
        columns = ", ".join(
            [f"{column_name} {data_type}" for column_name, data_type in schema.items()]
        )
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
        self.execute_sql(sql)

    def table_exists(self, table_name: str) -> bool:
        """
        Checks if a table exists in the database.

        :param table_name: The name of the table to check for.
        :return: True if the table exists, False otherwise.
        """
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,),
        )
        return bool(self.cursor.fetchone())

    def create_table_if_needed(self, table_name: str, schema: Dict[str, str]):
        """
        Creates a table with the specified schema if it does not exist. If the table exists, it checks if the existing
        schema matches the expected schema.

        :param table_name: The name of the table to potentially create.
        :param schema: The schema of the table to create.
        """
        if not self.table_exists(table_name):
            self.create_table(table_name, schema)
        else:
            if not self.table_schema_matches(table_name, schema):
                print(
                    f"Table '{table_name}' exists but schema does not match. Consider updating the schema manually."
                )
                # Here you could add logic to alter the table schema as needed.

    def insert_into_table(
        self, table_name: str, data: Dict[str, Any], on_conflict: str = "ignore"
    ):
        """
        Inserts data into a specified table, with an option to ignore or replace duplicates.

        :param table_name: Name of the table where data will be inserted.
        :param data: A dictionary of the data to insert.
        :param on_conflict: Strategy for handling conflicts - "ignore" to skip duplicates, "replace" to update existing.
        """
        # Validate the on_conflict parameter to ensure it's either "ignore" or "replace"
        if on_conflict not in ["ignore", "replace"]:
            raise ValueError("on_conflict must be either 'ignore' or 'replace'")

        # Convert lists to strings
        for key, value in data.items():
            if isinstance(value, list):
                # Convert list to a string representation
                # You can customize this as needed, for example, using json.dumps(value) for a JSON string
                data[key] = ", ".join(map(str, value))

        placeholders = ", ".join(["?"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())
        sql = f"INSERT OR {on_conflict.upper()} INTO {table_name} ({columns}) VALUES ({placeholders})"
        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            print(f"Document inserted into '{table_name}': {data}")
        except sqlite3.Error as e:
            print(f"An error occurred inserting document into '{table_name}': {e}")

    def sync_data_from_mongodb(
        self,
        mongo_db: str,
        collection_name: str,
        table_name: str,
        schema: Dict[str, str],
        filter_criteria: Dict[str, Any] = None,
    ):
        """
        Pulls data from MongoDB based on a specified collection and optional filter criteria,
        then inserts the data into an SQLite table according to a predefined schema. Also prints the number of documents found.

        :param mongo_db: The name of the MongoDB database to query.
        :param collection_name: The name of the MongoDB collection to query.
        :param table_name: The name of the SQLite table where data will be inserted.
        :param schema: The schema defining which fields to include and their data types.
        :param filter_criteria: Optional MongoDB filter criteria to select documents. Defaults to None, fetching all documents.
        """
        mongodb_utility = MongoDBUtilitySingleton(db_name=mongo_db)
        documents = mongodb_utility.db[collection_name].find(
            filter_criteria if filter_criteria is not None else {}
        )

        # Count the number of documents found
        num_documents = documents.count()
        print(
            f"Found {num_documents} documents in MongoDB collection '{collection_name}'."
        )

        for doc in documents:
            # Prepare data for insertion based on the schema
            data = {key: doc.get(key) for key in schema.keys() if key in doc}
            self.insert_into_table(table_name, data, on_conflict="ignore")

    def export_table_to_csv(self, table_name: str, csv_file_path: str):
        """
        Exports a table to a CSV file using pandas.

        Parameters:
        - table_name (str): The name of the SQLite table to export.
        - csv_file_path (str): The file path where the CSV should be saved.

        Returns:
        None
        """
        try:
            # Query the entire table
            query = f"SELECT * FROM {table_name}"
            # Use pandas read_sql_query method to convert SQL table to DataFrame
            df = pd.read_sql_query(query, self.conn)

            # Export DataFrame to CSV
            df.to_csv(csv_file_path, index=False)
            print(f"Table '{table_name}' successfully exported to '{csv_file_path}'.")
        except Exception as e:
            print(f"An error occurred while exporting '{table_name}' to CSV: {e}")

    def close(self):
        self.conn.close()


# Example usage
