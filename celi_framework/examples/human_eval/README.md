
To run the HumanEval data set, use the following JobDescription (probably set in your .env file): 

`JOB_DESCRIPTION=celi_framework.examples.human_eval.job_description.job_description`

Running `python -m celi_framework.examples.human_eval.eval <file>` with the name of the output file writes out results.

The current run produces 88.89% correct results on HumanEval.  