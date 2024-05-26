import sys

from celi_framework.examples.human_eval.tools import HumanEvalTools
from celi_framework.utils.utils import read_json_from_file, get_most_recent_file

# Evaluate results
if len(sys.argv) > 1:
    file = sys.argv[1]
else:
    directory = "target/celi_output/drafts"
    file = get_most_recent_file(directory)
    # file = "celi_framework/examples/human_eval/example_output_gpt-4-0125-preview.json"
    # file = "celi_framework/examples/human_eval/gpt_only_example.json"

print(f"Evaluating {file}")
results = read_json_from_file(file)
tools = HumanEvalTools()


def run_test(id, solution):
    code = tools.tests.loc[id, "prompt"] + "\n" + solution["func"]
    return tools._run_official_tests(id, code)


evaluated = {k: run_test(k, v) for k, v in results.items()}

total = tools.tests.shape[0]
n_trials = len(evaluated)
n_correct = len([_ for _ in evaluated.values() if _ is None])
errors = {k: v for k, v in evaluated.items() if v is not None}
unevaluated = total - n_trials

print(f"{n_correct} correct out of {n_trials}: {round(100*n_correct/n_trials, 2)}%")
print(f"Unanswered: {unevaluated} - resulting in {round(100*n_correct/total, 2)}%")
print("Errors:\n")
for k, v in errors.items():
    print(f"{k}:{v}\n")
