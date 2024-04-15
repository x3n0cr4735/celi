"""
Module: celi_framework.post-monitor

This script is an initial version designed to facilitate the evaluation and analysis of process execution data
within a given project. It currently includes functionalities for standardizing task labels within a dataset,
synchronizing evaluation data from MongoDB to an SQLite database, and exporting this data to CSV format.
Moreover, it provides capabilities for analyzing task quality variations based on specific criteria,
such as finish reason, and visualizing these variations through generated charts.

Note that this is a first-step version that needs to be further modularized and properly coded to work well
with the rest of the project.

This script contains several key components:
- `standardize_task_labels` function: Standardizes task labels in a DataFrame to a uniform format.
- `TaskQualityAnalysis` class: Loads evaluation data from a CSV file, prepares it for analysis, and plots
                               quality variation by finish reason.
- Utility functions `sync_evaluations_with_sql` and `export_csv`:  Synchronize MongoDB data with an SQLite
                                                                  database and export the data to a CSV file,
                                                                  respectively.
- Execution flow at the end of the script: Performs data preparation, synchronization, and analysis.

Key features include data standardization, database synchronization, and analytical visualization,
aimed at streamlining the evaluation process of process executions within a project.

TODOs:
- In the `plot_quality_variation_by_finish_reason` function, incorporate further data-checking mechanisms
  to ensure robustness, make the function more modular, allowing for more diversification in plotting mechanisms,
  develop efficient error-handling mechanisms, and include compatibility for other charting libraries
  to improve functionality and visual aesthetics.
- In the `sync_evaluations_with_sql` function, allow the MongoDB collection name, SQLite table name,
  and filtering criteria to be passed as arguments for better flexibility.
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from celi_framework.utils.sql_utils import ManageDB

CSV_PATH = "/Users/jwag/PycharmProjects/draft-0/output/evaluation_reports/process_executions.csv"
CHARTS_PATH = "/Users/jwag/PycharmProjects/draft-0/output/evaluation_reports/charts"


def standardize_task_labels(
    df: pd.DataFrame, task_column: str = "task"
) -> pd.DataFrame:
    """
    Standardizes task labels in the DataFrame to a 'Task X' format for labels that can be converted to integers.
    Labels that cannot be converted to integers are set to None, effectively ignoring them.

    Parameters:
        df (pd.DataFrame): A DataFrame containing the task data.
        task_column (str): The column in the DataFrame that contains the task labels. The default is 'task'.

    Returns:
        pd.DataFrame: The DataFrame with standardized task labels for integer-based tasks,
                      and None for non-integer labels.
    """

    def standardize_label(task_label):
        # Handle 'nan', NaN values, and ignore non-integer labels like '9.1.3'
        if pd.isnull(task_label) or task_label.strip().lower() == "nan":
            return None
        # Match labels that are strictly integers or have the 'Task #' format
        match = re.search(r"(task\s*#?\s*\[?\s*(\d+)\]?)", task_label, re.IGNORECASE)
        if match:
            return f"Task {int(match.group(2))}"  # Convert to integer to remove leading zeros
        elif (
            task_label.strip().isdigit()
        ):  # Directly prefix numeric strings with "Task"
            return f"Task {int(task_label)}"  # Convert to integer to standardize format
        # Return None for non-integer and complex formats
        return None

    df[task_column] = df[task_column].astype(str)  # Ensure all entries are strings
    df["standardized_task"] = df[task_column].apply(standardize_label)
    print(f"standarized_task unique values= {df['standardized_task'].unique()}")
    return df


# Corrected part of TaskQualityAnalysis class for loading data
class TaskQualityAnalysis:
    """
    A class that carries out the quality analysis of tasks. It loads the evaluation data from a
    CSV file, prepares the data for analysis including standardizing task labels, and provides
    methods to plot and analyze the quality variation by finish reason.

    Attributes:
        csv_path (str): The path to the CSV file containing the evaluation data.
        data (pd.DataFrame): The DataFrame which holds the evaluation data for analysis.

    Methods:
        load_data() -> pd.DataFrame:
            Loads and standardizes the task labels in the data.

        prepare_data() -> None:
            Prepares the data for analysis. This includes converting the 'version' column to numeric
            datatype and converting 'timestamp' column to datetime datatype.

        plot_quality_variation_by_finish_reason(finish_reason: str, charts_dir: str) -> None:
            Plots the quality metric variation over versions for tasks separated by the finish
            reason ('stop' or 'function_call'), and saves the plots to a specified directory.
    """

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.data = None

    def load_data(self) -> pd.DataFrame:
        """
                Loads the evaluation data from a CSV file, filters tasks with a 'stop' finish reason, and standardizes the task labels.
                Exception handling is implemented to manage issues during the data loading process.

        Returns:
                    pd.DataFrame: The loaded DataFrame with standardized task labels or an exception error in case of a problem.

                Raises:
                    Exception: An error occurred while loading data.
        """
        try:
            df = pd.read_csv(self.csv_path)
            df = df[df["finish_reason"] == "stop"]  # Corrected filtering expression
            df = standardize_task_labels(df)
            self.data = df
            self.prepare_data()
        except Exception as e:
            print(f"An error occurred while loading data: {e}")

    def prepare_data(self):
        """
        Prepares the data for analysis.
        Attempts to convert the 'version' column to numeric datatype and 'timestamp' column to datetime datatype, all while handling any potential errors during type conversion.
        Future data preparation steps should be added in this method.

        Returns:
             None: This method does not return but modifies the class attribute `data` in place.
        """
        if "version" in self.data.columns:
            self.data["version"] = pd.to_numeric(self.data["version"], errors="coerce")
        if "timestamp" in self.data.columns:
            self.data["timestamp"] = pd.to_datetime(
                self.data["timestamp"], errors="coerce"
            )
        # Add other data preparation steps here

    def plot_quality_variation_by_finish_reason(
        self, finish_reason: str, charts_dir: str
    ):
        """
        Plots the quality metric variation over the versions for tasks, by the given finish reason.
        The generated plots are saved to a specified directory.

        Parameters:
            finish_reason (str): The task finish reason to group tasks by, possible values are 'stop' or 'function_call'.
            charts_dir (str): The directory path to where the charts will be saved.

        Returns:
           None. The charts are saved directly to the charts_dir directory.
        """
        # Prepare data for charting
        self.prepare_data()

        # Create a new DataFrame filtered based on the provided finish reason
        filtered_data = self.data[self.data["finish_reason"] == finish_reason]

        # Determine the column label and metric for charting based on finish reason and assign them to variables
        if finish_reason == "stop":
            # For 'stop' finish reason, we use 'standardized_task' as label and 'rsp_overall_quality' as metric
            filtered_data["label"] = filtered_data["standardized_task"].astype(str)
            metric = "rsp_overall_quality"
            plot_title = "Task # Quality Variation Over Versions"
            file_name = "task_quality_variation_stop_v2.png"
        elif finish_reason == "function_call":
            # For 'function_call' finish reason, we use 'function_name' as label and 'rsp_accuracy' as metric
            filtered_data["label"] = filtered_data["function_name"]
            metric = "rsp_overall_quality"
            plot_title = "Function Call Accuracy Variation Over Versions"
            file_name = "task_quality_variation_function_call.png"
        else:
            # Print an error message for any other finish reasons and terminate the function
            print("Invalid finish_reason")
            return

        # Group by 'label' and 'version' columns, then calculate the mean of the selected metric
        quality_by_label_version = (
            filtered_data.groupby(["label", "version"])[metric].mean().reset_index()
        )
        # Sort them by 'label' and 'version'
        quality_by_label_version.sort_values(by=["label", "version"], inplace=True)

        # Create a new plot figure
        plt.figure(figsize=(14, 8))

        # Get the list of unique labels and assign them colors from the 'viridis' colormap
        unique_labels = quality_by_label_version["label"].unique()
        colors = plt.cm.viridis(np.linspace(0, 1, len(unique_labels)))

        # For each unique label, plot its data in its assigned color
        for label, color in zip(unique_labels, colors):
            label_data = quality_by_label_version[
                quality_by_label_version["label"] == label
            ]
            plt.plot(
                label_data["version"],
                label_data[metric],
                marker="o",
                linestyle="-",
                label=label,
                color=color,
            )

        # Set plot titles and labels
        plt.xlabel("Version", fontsize=14)
        plt.ylabel(f'Average {metric.replace("_", " ").title()}', fontsize=14)
        plt.title(plot_title, fontsize=16)
        plt.legend(title="Task Label", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.grid(True)
        plt.tight_layout()

        # Check if the directory to save charts exists, if not, create it
        if not os.path.exists(charts_dir):
            os.makedirs(charts_dir)

        # Save the chart to a file
        plt.savefig(os.path.join(charts_dir, file_name))

        # Close the figure to free up memory
        plt.close()

        # Print message indicating chart was saved
        print(f"Chart saved to {os.path.join(charts_dir, file_name)}")


def sync_evaluations_with_sql(
    collection_name="process_executions",
    table_name="process_executions",
    filter_criteria=None,
):
    """
    Synchronizes evaluation data from MongoDB to an SQLite database called 'test_evaluations.db' by
    creating a new 'process_executions' table or updating the existing one.

    Automatically creates 'test_evaluations.db' if it does not exist and ensures that the 'process_executions'
    table is updated in this database. This function maintains a synchronized state of data between MongoDB and SQLite.

    Returns:
        None. The output is a 'process_executions' table in 'test_evaluations.db' updated with the MongoDB data.
    """
    db = ManageDB("test_evaluations.db")

    # TODO -> Put this in a config
    process_executions_schema = {
        "_id": "TEXT",
        "id": "TEXT",
        "id_is": "TEXT",
        "id_is_hash_of": "TEXT",
        "version": "INT",
        "prompt_id": "TEXT",
        "process_id": "TEXT",
        "template_id": "TEXT",
        "finish_reason": "TEXT",
        "document_section": "TEXT",
        "task": "TEXT",
        "task_desc": "TEXT",
        "prompt_exception": "INTEGER",
        "function_name": "TEXT",
        "function_arguments": "TEXT",
        "timestamp": "TEXT",
        "rsp_relevance": "INTEGER",
        "rsp_accuracy": "INTEGER",
        "rsp_completeness": "INTEGER",
        "rsp_clarity": "INTEGER",
        "rsp_integration": "INTEGER",
        "rsp_contextual_sufficiency": "INTEGER",
        "rsp_overall_quality": "INTEGER",
    }

    # db.create_table('process_executions', process_executions_schema)
    # Ensure the SQLite table exists
    db.create_table_if_needed("process_executions", process_executions_schema)

    # TODO -> Enable filtering

    # Sync data from MongoDB to SQLite
    db.sync_data_from_mongodb(
        "test_db",
        collection_name=collection_name,
        table_name=table_name,
        schema=process_executions_schema,
    )

    print(
        f"Completed syncing documents from MongoDB collection '{collection_name}' to SQLite table '{table_name}'."
    )

    db.close()


def export_csv():
    """
    Exports 'process_executions' table from SQLite database to a CSV file.

    Exports each available table in the SQLite database to separate CSV files in the specified directory,
    allows for easy access and manual analysis of data for evaluation purposes.

    Returns:
         None. The output is the CSV file saved in the specified directory.
    """
    db = ManageDB()
    db.export_table_to_csv(table_name="process_executions", csv_file_path=CSV_PATH)
    db.close()


def prep_data():
    """
    Prepares the data for analysis.

    Syncs the data from MongoDB to SQLite, exports the data from SQLite to CSV and loads the standardized task
    labels data to be used for analysis. It's mainly designed to sync the data and ready it for analysis.

    Returns:
         None. The output is an updated SQLite database and CSV file with the latest data.
    """
    # Prep data
    sync_evaluations_with_sql()
    export_csv()


if __name__ == "__main__":
    prep_data()  # Make sure this is called to sync and export data before analysis

    analysis = TaskQualityAnalysis(CSV_PATH)
    analysis.load_data()  # Load and standardize task labels

    # Ensure that data is not None before plotting
    if analysis.data is not None and not analysis.data.empty:
        # Plot and save charts for tasks with 'stop' finish reason
        analysis.plot_quality_variation_by_finish_reason("stop", CHARTS_PATH)

        # Plot and save charts for tasks with 'function_call' finish reason
        analysis.plot_quality_variation_by_finish_reason("function_call", CHARTS_PATH)
