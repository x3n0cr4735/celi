"""
The `utils.synthetic_data` module provides functionalities for generating synthetic data to support testing and evaluation
of embeddings and NLP models. This module is particularly useful for simulating various textual inputs and scenarios
that models might encounter in real-world applications. It includes methods for creating synthetic queries,
applying synonyms to alter textual content, and generating structured data resembling tables for embedding testing.
Features:
- `generate_varied_synthetic_queries`: Generates a list of synthetic queries by applying a set of templates to a given answer, creating varied textual representations.
- `utilize_generate_varied_synthetic_queries`: Utilizes `generate_varied_synthetic_queries` to generate synthetic data based on original data and saves the generated data to a JSON file.
- `generate_synthetic_queries_v2`: A more advanced version of synthetic query generation that uses rephrasing templates and incorporates both the original question and answer for context.
- `utilize__synthetic_queries_v2`: Applies `generate_synthetic_queries_v2` on a dataset to produce synthetic queries and saves them to a JSON file.
- `apply_synonyms`: Replaces words in a given text with their synonyms based on a predefined synonym dictionary, creating textual variations.
- `generate_table`: Simulates the generation of synthetic table data based on demographics, efficacy, safety, and lab measures. This function constructs a pandas DataFrame with synthetic table entries, demonstrating how structured data might be used in testing embeddings or model responses.
"""

import random
import numpy as np
import pandas as pd

# ------ Synthetic data for embedding testing ----------------------------------------------------------


# Test 1
# Function to generate synthetic queries using templates
def generate_varied_synthetic_queries(answer):
    # List of templates for generating synthetic queries
    templates = [
        "What is the term for {answer}?",
        "What is known as {answer}?",
        "Can you name an entity known for {answer}?",
        "Identify the term associated with {answer}.",
        "What is the common term referred to as {answer}?",
        "Which term is synonymous with {answer}?",
        "What do you call {answer}?",
        "Name the term that corresponds to {answer}.",
        "What is another term for {answer}?",
        "What is the technical term for {answer}?",
    ]

    # Generate synthetic queries by substituting the answer into each template
    synthetic_queries = [template.format(answer=answer) for template in templates]
    return synthetic_queries


def utilize_generate_varied_synthetic_queries(file_path, original_data):
    # Generate varied synthetic data
    varied_synthetic_data = []
    for dat in original_data:
        answer = dat["Answer"]
        synthetic_queries = generate_varied_synthetic_queries(answer)
        original_query = dat["Question"]
        for synthetic_query in synthetic_queries:
            varied_synthetic_data.append(
                {
                    "synthetic_query": synthetic_query,
                    "expected_answer": answer,
                    "original_query": original_query,
                }
            )
    # Save the varied synthetic data to a new JSON file
    with open(file_path, "w") as f:
        json.dump(varied_synthetic_data, f, indent=4)


# Test 2 ----------------------
# Define function to generate synthetic queries based on the original question and answer
def generate_synthetic_queries_v2(original_question, answer):
    # List of rephrasing templates
    # Each template has placeholders for the original question or answer
    templates = [
        "Could you tell me which {answer_placeholder} corresponds to: {question_placeholder}?",
        "In reference to: {question_placeholder}, what is the {answer_placeholder}?",
        "Relating to: {question_placeholder}, identify the {answer_placeholder}.",
        "Regarding: {question_placeholder}, can you name the {answer_placeholder}?",
        "With respect to: {question_placeholder}, what is the {answer_placeholder}?",
    ]
    # Generate synthetic queries by substituting the placeholders with the actual question or answer text
    synthetic_queries = [
        template.format(
            question_placeholder=original_question, answer_placeholder=answer
        )
        for template in templates
    ]
    return synthetic_queries


def utilize__synthetic_queries_v2(file_path, original_data):
    # Generate synthetic data---------
    synthetic_data_varied_v2 = []
    for dat in original_data:
        original_question = dat["Question"]
        answer = dat["Answer"]
        # Generate synthetic queries using the function
        synthetic_queries = generate_synthetic_queries_v2(original_question, answer)
        for synthetic_query in synthetic_queries:
            synthetic_data_varied_v2.append(
                {
                    "synthetic_query": synthetic_query,
                    "expected_answer": answer,
                    "original_query": original_question,
                }
            )
    # Save the varied synthetic data to a new JSON file
    with open(file_path, "w") as f:
        json.dump(synthetic_data_varied_v2, f, indent=4)


# Test 3 --------------------------
# Define a simple synonym dictionary
synonym_dict = {
    "glucose": "blood sugar",
    "organ": "body part",
    "mammal": "animal",
    "gavial": "gharial",
    "crocodile": "crocodilian",
    "eland": "antelope",
    "rattlesnake": "pit viper",
    "metal": "alloy",
    "molecular": "atomic",
    "structure": "arrangement",
    "tropospheric": "lower atmospheric",
    "plane": "aircraft",
    "sound barrier": "sonic barrier",
}


def apply_synonyms(text, synonym_dict):
    """Function to replace words in text with their synonyms."""
    for word, synonym in synonym_dict.items():
        text = text.replace(word, synonym)
    return text


# ------------------------


def generate_table():
    # List of features for each measures
    demographics = [
        "Age < 50",
        "Age 50-70",
        "Age > 70",
        "Female",
        "Male",
        "White/Caucasian",
        "African American",
        "Asian",
    ]
    efficacy = [
        "MTD/RP2D",
        "Tolerability",
        "PK profile",
        "Immunogenicity",
        "Preliminary anti-lymphoma efficacy - Lugano",
        "Preliminary anti-lymphoma efficacy - LYRIC",
    ]
    safety = [
        "DLTs",
        "AEs",
        "Cytokine measures",
        "Lab parameters",
        "PK parameters",
        "ADAs incidence",
    ]
    labs = [
        "PK parameters (clearance, volume of distribution, etc.)",
        "Incidence of anti-drug antibodies (ADAs) to [IMP]",
        "Expression of CD3, CD20, and other molecular markers in tumor biopsies pre-treatment",
    ]

    # Dictionary to hold different set of measures
    measure_dict = {
        "demographics": demographics,
        "efficacy": efficacy,
        "safety": safety,
        "labs": labs,
    }

    # Groups for comparison
    groups = {"two-arm": ["24mg", "48mg"], "three-arm": ["Dose 1", "Dose 2", "Dose 3"]}

    # Sample sizes to select from
    sample_sizes = ["All Patients", "Subset of Patients"]

    # Efficacy and Safety levels
    eff_saf_levels = ["0", "1"]

    # Container for storing tables data
    tables = []

    # Loop to generate tables for each measure type and group
    for measure_type in measure_dict.keys():
        for group_type in groups.keys():
            for _ in range(10):  # Generate 10 tables for each combination
                # Select a random sample size
                sample_size = random.choice(sample_sizes)

                for group in groups[group_type]:
                    # Select a random feature for this measure type
                    feature = random.choice(measure_dict[measure_type])

                    # Create a dictionary for the feature
                    for level in eff_saf_levels:
                        feature_dict = {
                            "Arms": f"{len(groups[group_type])} arms",
                            "Measures": feature,
                            "Sample": sample_size,
                            "Significant": "Yes" if random.random() > 0.5 else "No",
                            "Efficacy": level
                            if measure_type in ["efficacy", "safety"]
                            else np.nan,
                            "Safety": level
                            if measure_type in ["efficacy", "safety"]
                            else np.nan,
                            "Group": group,
                        }

                        # Add feature_dict to tables list
                        tables.append(feature_dict)

    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(tables)

    # # Save DataFrame to CSV
    # embeddings_files.to_csv('tables.csv', index=False)

    # print("CSV file has been saved as 'tables.csv'")

    return df
