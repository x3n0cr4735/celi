import sys

from celi_framework.examples.human_eval.tools import HumanEvalTools
from celi_framework.utils.utils import read_json_from_file


def run_test(id, solution, tools):
    code = tools.tests.loc[id, "prompt"] + "\n" + solution["func"]
    return tools._run_official_tests(id, code)


def main(file_path):
    """
    Runs the main function to evaluate the results from a JSON file.

    Parameters:
        file_path (str): The path to the JSON file containing the results.

    Returns:
        None

    This function reads the JSON file specified by the `file_path` parameter and
    evaluates the results using the `HumanEvalTools` class. It then calculates the
    number of correct and incorrect results and prints the percentage of correct
    results. It also prints the errors, along with their corresponding keys.

    Note:
        This function assumes that the JSON file contains a dictionary-like structure
        with keys and values.

    Example usage:
        main("path/to/results.json")
    """
    results = read_json_from_file(file_path)
    tools = HumanEvalTools()

    evaluated = {k: run_test(k, v, tools) for k, v in results.items()}

    n_trials = len(evaluated)
    n_correct = len([_ for _ in evaluated.values() if _ is None])
    errors = {k: v for k, v in evaluated.items() if v is not None}

    print(
        f"{n_correct} correct out of {n_trials}: {round(100 * n_correct / n_trials, 2)}%"
    )
    print("Errors:\n")
    for k, v in errors.items():
        print(f"{k}: {v}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = (
            "celi_framework/examples/human_eval/example_output_gpt-4-0125-preview.json"
        )

    main(file)
