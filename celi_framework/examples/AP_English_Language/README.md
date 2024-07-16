# AP Language Tasks Assitant.

## Overview

This project implements AP (Advanced Placement) English Language and Composition tasks using CELI. The AP Language exam assesses students' ability to analyze texts, construct arguments, and demonstrate sophisticated writing skills.

## Quick Start

To run CELI for AP Language tasks:

1. Set up your environment:
   - Ensure your `.env` file is correctly configured (refer to `.env.example`).
   - Set `JOB_DESCRIPTION=celi_framework.examples.AP_English_Language.job_description.job_description` in your `.env` file.

2. Run the task:
   - From the root of the project directory, execute:
     ```
     python -m celi_framework.main
     ```
   - This will generate output files in `ap_language/target/celi_output/`.

3. Evaluate the results:
   - Use the AP English Language and Composition scoring rubrics to assess the generated responses. See `data/scoring_guidelines/set_1_target_q1_scoring.txt`

## AP Language Task Types

CELI is designed to handle the three main types of free-response questions in the AP English Language exam:

1. Synthesis Essay
2. Rhetorical Analysis
3. Argument Essay

Each task type requires different analytical and writing skills, which CELI is trained to emulate.

## Project Structure

```
ap_language/
├── data/scoring_guidelines/set_1_target_q1_scoring.txt
├── job_description.py
├── tools.py
├── eval.py
└── README.md
```

## Key Features

- Emulates advanced high school/early college-level writing skills
- Analyzes complex texts and constructs arguments
- Adheres to AP Language rubrics and expectations
- Handles various prompt types and source materials

## Evaluation Criteria

CELI's output is evaluated based on the official AP Language and Composition scoring guidelines, which typically assess:

1. Thesis development
2. Evidence and commentary
3. Sophistication of thought
4. Writing quality and clarity


## Acknowledgments

- College Board for AP English Language and Composition curriculum and exam structure

For more information on the AP English Language and Composition exam, visit: https://apstudents.collegeboard.org/courses/ap-english-language-and-composition