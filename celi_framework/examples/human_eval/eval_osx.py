import sys

from celi_framework.examples.human_eval.tools import HumanEvalTools
from celi_framework.utils.utils import read_json_from_file


def run_test(id, solution, tools):
    code = tools.tests.loc[id, "prompt"] + "\n" + solution["func"]
    return tools._run_official_tests(id, code)


def main(file_path):
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
