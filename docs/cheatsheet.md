# Cheatsheet

The following cheatsheet provides some example command lines for common cases.

|-----------------------|----------------------------------|
| Use                   | Example Command                  |
+=======================+==================================+
| Run the basic example | ```python -m celi_framework.main \  |
|                       |      --job-description=celi_framework.examples.human_eval.job_description.job_description |
+-----------------------------------------+-----------------------------------------------+
| Pass parameters to the  | ```python -m celi_framework.main \  |
| ToolImplmentations class    |      --job-description=celi_framework.examples.human_eval.job_description.job_description |
|                             |      --tool-config='{"single_example":"HumanEval/3"}'                |
+-----------------------------------------+-----------------------------------------------+
| Pass parameters to the  | ```python -m celi_framework.main \  |
| use Claude models    |      --job-description=celi_framework.examples.human_eval.job_description.job_description |
|                         |    --anthropic-api-key=<Insert you ANthropic API key here>                |
|                         |    --primary-model-name=claude-3-5-sonnet-20240620                |
+-----------------------------------------+-----------------------------------------------+
| Turn off parallelization  | ```python -m celi_framework.main \  |
| and caching for debugging    |      --job-description=celi_framework.examples.human_eval.job_description.job_description |
|                         |    --no-cache --serialize                |
+-----------------------------------------+-----------------------------------------------+
| Set the size of an individual LLM response to 4096    | ```python -m celi_framework.main \  |
| and a total limit of 1M input and output tokens.    |      --job-description=celi_framework.examples.human_eval.job_description.job_description |
|                                                       |    --max-tokens=4096 --token-budget=1000000                |
+-----------------------------------------+-----------------------------------------------+
