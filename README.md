[![PyPI version](https://badge.fury.io/py/celi-framework.svg)](https://badge.fury.io/py/celi-framework)
[![Tests](https://github.com/x3n0cr4735/celi/actions/workflows/tests.yml/badge.svg)](https://github.com/x3n0cr4735/celi/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/celi/badge/?version=latest)](https://celi.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Versions](https://img.shields.io/pypi/pyversions/celi-framework)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

![CELI Logo](docs/CELI_README_Header_Picture.png)

 <!-- start elevator-pitch -->
# CELI: A Framework for Controller-Embedded Language (Model) Interactions

**CELI** (Controller-Embedded Language (Model) Interactions, pronounced 'Kelly') is a framework that integrates LLM controllers to enhance and automate a wide range of tasks and processes. It offers:

- 🛠️ **Versatile Application:** Handles diverse tasks such as automated document generation, data pipelines, building robust software, and more.
- 🧠 **Intelligent Automation:** Empowers users to strategically integrate LLMs into complex projects.
- 🔄 **Dynamic Adaptability:** Adjusts strategies in real-time based on context and feedback.
- 📈 **Scalable Architecture:** Efficiently handles projects of all sizes, from quick scripts to enterprise-level applications.
- 🔧 **Customizable Core:** Allows developers to tailor CELI's capabilities to specific industry needs.

Whether you're automating document generation, streamlining complex data processing pipelines, or hardening software applications, CELI provides a flexible, powerful framework to enhance your productivity.

🔗 [Join our Discord](https://discord.gg/Cr4JKKFH2X) | 🔗 [Read our Docs](https://celi.readthedocs.io/en/latest/)

**Important:** CELI is currently in alpha. For support, join our Discord server or submit an issue on this GitHub repo.


<!-- end elevator-pitch -->

## Table of Contents

1. [Introduction](#celi-a-framework-for-controller-embedded-language-model-interactions)
2. [Quick Start](#quick-start)
3. [CELI Overview](#celi-overview)
4. [What is CELI?](#what-is-celi)
5. [Discord Server](#discord-server)
6. [Documentation](#documentation)
7. [Contributing](#contributing)
8. [License](#license)

<!-- start getting-started -->

## Quick Start
### Prerequisites
- Python 3.10, 3.11 or 3.12
- pip

### Installation
```bash
pip install celi-framework
````
### Run a Simple Demo (no LLM-setup required):
```bash
  python -m celi_framework.main \
  --job-description=celi_framework.examples.human_eval.job_description.job_description \
  --tool-config='{"single_example":"HumanEval/3"}' \
  --simulate-live
```

This example simulates using CELI to solve problem #3 of the HumanEval benchmark programming problem set.  It uses 
cached versions of the LLM outputs so it doesn't require an API key or make any paid LLM calls on your behalf.  The 
result will be put in the `target/drafts` directory.

Running this demo should take a few minutes. You will be able to see how CELI tackles the problem and the LLM calls
it makes, along with the responses.

### Explore the Results
Check the output in the `target/drafts` directory.

### Run the Example Live
The code above uses a cached version of the LLM results. To meaningfully run CELI on anything new, you will need to make new LLM calls, which will require an OpenAI API key (or your own local LLM; see [LLM Support](https://celi.readthedocs.io/en/latest/llm_support.html)).
```bash
  python -m celi_framework.main \
  --job-description=celi_framework.examples.human_eval.job_description.job_description \
  --openai-api-key=<Insert your OpenAI API key here> \
```

Again, you can check your output in the `target/drafts` directory.

<!-- end getting-started -->

## CELI Overview

### Core Modules
Located in the `celi_framework.core` package, the following essential core modules facilitate CELI's primary operations:

- **Processor**: Manages and orchestrates the drafting of documents using language models, acting as the core of the CELI system.
- **Monitor**: Observes and evaluates the performance of the ProcessRunner, ensuring quality and efficiency in automated tasks.
- **Job Description**: Manages a comprehensive list of user-defined job descriptions that guide how tasks are executed.
- **Tools**: Provides mechanisms for CELI to interact with external systems and can be customized to suit specific use cases.

### Example Use Cases
For practical applications and demonstrations, explore the `celi_framework.examples` package [here](https://github.com/x3n0cr4735/celi/tree/main/celi_framework/examples).

### Creating Your Own Project Using CELI

Users extend the CELI framework by defining their own job descriptions and tools. These user-defined modules leverage and extend the functionalities of the core modules. This allows for a high degree of customization and tailoring to specific needs:

- **User-Defined Job Descriptions**: Users can create unique job descriptions that specify detailed instructions and operational steps, ensuring that automated processes align closely with project requirements.
- **Custom Tool Implementations**: Developers can implement custom tools by importing core modules and utilizing their functionalities. These tools can be adapted to integrate seamlessly with existing systems or to introduce new capabilities.

For more detailed instructions see the Documentation [here](https://celi.readthedocs.io/en/latest/new_use_cases.html).

## What is CELI?

CELI (Controller-Embedded Language Interactions) is a framework that automates complex projects using Large Language Models (LLMs). It decomposes projects into sets of tasks and utilizes LLM-directed controller logic for execution. Key features include:

### 🔄 Dynamic Workflow Management
- Supports complex workflows with nested operations and recursion
- Adapts tasks based on contextual changes or external inputs

### ⚙️ Integrated Control Logic
- Embeds controller logic within LLM prompts
- Manages multi-layered tasks with reduced manual intervention

### 🏗️ Task Structuring
- Employs a structured pseudo-code approach
- Enables precise execution of complex operations

### 🔁 Recursive Task Handling
- Efficiently manages multiple layers of tasks
- Allows for adaptation to operational challenges

### 🌐 Active Data Management
- Incorporates function calls (e.g. vector or SQL DB calls) within operational prompts
- Facilitates real-time data interactions

### 📈 Scalable Framework
- Handles a range of project sizes and complexities
- Supports diverse requirements while maintaining performance

### 💡 LLM-OOP Integration
- Embeds the LLM controller within Object-Oriented Programming (OOP) structures
- Enables direct interaction between OOP functions and the LLM controller
- Facilitates interactions with external systems (APIs, databases, LLM agents)

This architecture distinguishes CELI from *traditional agent-based frameworks*, offering an integrated approach to automated knowledge work.

## Discord Server

[Join our Discord server](https://discord.gg/Cr4JKKFH2X) to discuss the project with users, contributors, and project authors.

## Documentation

Explore the rest of the documentation to learn more about CELI.
* [Getting Started](https://celi.readthedocs.io/en/stable/getting_started.html) - Learn more about the various ways to run CELI.
* [Running CELI](https://celi.readthedocs.io/en/stable/running_celi.html) - Learn more about the various ways to run CELI.
* [New Use Cases](https://celi.readthedocs.io/en/stable/new_use_cases.html) - Learn how to apply CELI to your own use case.
* [API Reference](https://celi.readthedocs.io/en/stable/reference/index.html) - If you are into reading API docs directly.

## Contributing

If you would like to contribute to the development of CELI, we welcome contributions of all forms.  For more information on contributing, see the [contributor guidelines](https://celi.readthedocs.io/en/stable/contributing/index.html).

## License

CELI is licensed under the MIT License. Feel free to use, modify, and distribute the framework as per the license terms.
