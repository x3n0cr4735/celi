# Quick start
To run CELI against the **HumanEval** benchmark, use the following JobDescription (probably set in your .env file): 
- Make sure your .env is set up correctly (look at .env.example) and set `JOB_DESCRIPTION=celi_framework.examples.human_eval.job_description.job_description` specifically.
- From a terminal, and from the human_eval project directory, run `python main.py`. This will output a json file (with timestamp) with the answers in human_eval/target/celi_output/drafts. That's the "output file".
- To see what score you got, from a terminal, run `python eval.py <output file>` for windows, or `python eval_osx.py <output file>` for OS X (and probably Linux).