# Quick start
To run CELI against the **HumanEval** benchmark, use the following JobDescription (probably set in your .env file): 
- Make sure your .env is set up correctly (look at .env.example) and set `JOB_DESCRIPTION=celi_framework.examples.human_eval.job_description.job_description` specifically.
- From a terminal, and from the human_eval project directory, run `python main.py`. This will output a json file (with timestamp) with the answers in human_eval/target/celi_output/drafts. That's the "output file".
- To see what score you got, from a terminal, run `python eval.py <output file>` for windows, or `python eval_osx.py <output file>` for OS X (and probably Linux).

# Results

With gpt-4-0125-preview
150 correct out of 163: 92.02%
Unanswered: 1 - resulting in 91.46%

With GPT-4o
145 correct out of 158: 91.77%
Unanswered: 6 - resulting in 88.41%

With gpt-4-turbo-2024-04-09
145 correct out of 159: 91.19%
Unanswered: 5 - resulting in 88.41%

0-shot GPT-4o only
110 correct out of 161: 68.32%
Unanswered: 3 - resulting in 67.07%

This is consistent with the GPT-4o technical report.
