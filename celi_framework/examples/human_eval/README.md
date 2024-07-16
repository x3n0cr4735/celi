Here's a structured README for the Human Eval benchmark project, incorporating the information you provided:

# Human Eval Benchmark for CELI

## Overview

This project implements the Human Eval benchmark using CELI. Human Eval is a benchmark for evaluating the code generation capabilities of language models.

## Quick Start

To run CELI against the HumanEval benchmark:

1. Set up your environment:
   - Ensure your `.env` file is correctly configured (refer to `.env.example`).
   - Set `JOB_DESCRIPTION=celi_framework.examples.human_eval.job_description.job_description` in your `.env` file.

2. Run the benchmark:
   - From the root of the project directory, execute:
     ```
     python -m celi_framework.main
     ```
   - This will generate a JSON output file (with timestamp) in `human_eval/target/celi_output/drafts/`.

3. Evaluate the results:
   - For Windows:
     ```
     python eval.py <output_file>
     ```
   - For OS X (and probably Linux):
     ```
     python eval_osx.py <output_file>
     ```

## Model Performance Comparison

### Performance Comparison Table

| Model                   | Correct | Total | Accuracy (%) | Unanswered | Resulting Accuracy (%) |
|-------------------------|---------|-------|--------------|------------|------------------------|
| gpt-4-0125-preview      | 150     | 163   | 92.02        | 1          | 91.46                  |
| GPT-4o                  | 145     | 158   | 91.77        | 6          | 88.41                  |
| gpt-4-turbo-2024-04-09  | 145     | 159   | 91.19        | 5          | 88.41                  |
| 0-shot GPT-4o only      | 110     | 161   | 68.32        | 3          | 67.07                  |

### Notes

- This performance data is consistent with the GPT-4o technical report.

## Project Structure

```
human_eval/
├── target/
│   └── celi_output/
│       └── drafts/
├── eval.py
├── eval_osx.py
├── job_description.py
├── tools.py
└── README.md
```


# The CELI Job Description

The overall use case is defined in the CELI Job Description object.  When you run CELI, you pass general configuration parameters and a Job Description to the main CELI processor.  The `JobDescription` defines the tasks to be accomplished and the tools to be run.  See (job_description.py)[celi-framework/core/job_description.py] for full details.

The job description contains several prompt strings which describe the overall job to be run at a high level along with any general guidance for the agent.  It also contains a `task_list` and a `tool_implementations_class`.

The `task_list` is a list of `Task` objects.  When completing a job, the agent will tackle each task in this list in order.  Each task has a name and a set of details.  The details is a dictionary that will be passed directly to the LLM to describe how to accomplish the task.  

The `tool_implementations_class` is a reference to a class that derives from `ToolImplementations` and contains the tools that the LLM can use to accomplish the task.  This class is described in the next section.


## About Human Eval Benchmark
The Human Eval benchmark is a widely-used tool for evaluating the code generation capabilities of large language models (LLMs). Key features include:

1. 164 hand-written Python programming problems
2. Each problem includes a function signature, docstring, and unit tests
3. Evaluates model's ability to complete function bodies correctly
4. Uses "pass@k" metric to measure performance

### For more information:

[The original paper](https://arxiv.org/abs/2107.03374)
[Official GitHub Repository](https://github.com/openai/human-eval?tab=readme-ov-file)
