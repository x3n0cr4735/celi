import sys

from celi_framework.examples.human_eval.tools import HumanEvalTools
from celi_framework.utils.utils import read_json_from_file

# Evaluate results
if len(sys.argv) > 0:
    file = sys.argv[1]
else:
    file = 'target/celi_output/drafts/2024-05-06_07-38-23.json'
results = read_json_from_file(file)
tools = HumanEvalTools()

def run_test(id, func):
    code = tools.tests.loc[id, 'prompt']+'\n'+func
    return tools.run_tests(id,code)

evaluated = {k : run_test(k, v) for k,v in results.items()}

n_trials = len(evaluated)
n_correct = len([_ for _ in evaluated.values() if _ is None])
errors = {k:v for k,v in evaluated.items() if v is not None}


print(f"{n_correct} correct out of {n_trials}: {round(100*n_correct/n_trials, 2)}%")
print("Errors:\n")
for k,v in errors.items():
    print(f"{k}:{v}\n")
