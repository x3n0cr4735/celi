[![PyPI version](https://badge.fury.io/py/celi-framework.svg)](https://badge.fury.io/py/celi-framework)
[![Tests](https://github.com/x3n0cr4735/celi/actions/workflows/tests.yml/badge.svg)](https://github.com/x3n0cr4735/celi/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/celi/badge/?version=latest)](https://celi.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Versions](https://img.shields.io/pypi/pyversions/celi-framework)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

<!-- start elevator-pitch -->
# CELI: Controller-Embedded Language Interactions

**CELI (pronounced 'Kelly')** is a framework designed for the automation of a diverse array of knowledge work tasks. Leveraging the analytical and computational capabilities of large language models (LLMs), CELI facilitates:

- **Autonomous Operation:** Unlike traditional agent-based frameworks, CELI embeds controller logic directly within LLM prompts. This unique approach enables CELI to operate autonomously, adjusting its strategies in real-time to handle errors, incongruencies, and multi-step decision-making without requiring human intervention. CELI's ability to self-correct and adapt ensures continuous progress and efficiency in automated tasks, making it exceptionally suited for complex applications.

- **Flexible Task Automation:** Enables automation across a broad spectrum of tasks, including but not limited to drafting complex documents, conducting systematic literature reviews, data analysis and summarization, and much more.

- **Scalability:** Designed to accommodate projects of any scale, CELI efficiently processes massive datasets and documents, and produces output of any size, making it an ideal solution for both targeted tasks and large-scale knowledge work automation.

- **Streamlined Document Lifecycle Management:** CELI optimizes the entire lifecycle of document processing, encompassing pre-processing, embedding, synthesis, content generation, and quality monitoring.

- **Development Flexibility:** CELI is architecturally designed to support developers in creating bespoke applications that conform to specific industry standards, including compliance, methodological rigor, and auditing requirements. This fosters innovation in the field of automated knowledge work by providing a scalable framework that integrates seamlessly into enterprise ecosystems.

[Join our Discord server](https://discord.gg/C5SQNdzV) to ask questions or get involved in our project!

Note: CELI is currently in alpha. If there are any issues installing, running, or utilizing CELI in your projects please let us know on Discord or create an issue or pull request. We will get back to you promptly.

## Goals

The CELI (Controller-Embedded Language Interactions) framework aims to empower users across various industries and domains with tools to automate routine and complex tasks efficiently. Our objectives are encapsulated in the following goals:

### Streamline Task Automation
- **Empower Efficiency**: Automate both routine and complex tasks to significantly reduce time and effort, enabling a focus on higher-value activities.
- **Boost Productivity**: By minimizing manual task execution, CELI enhances productivity, allowing users to allocate more time to strategic and creative endeavors.

### Enhance Quality and Accuracy
- **Improve Output Quality**: CELI ensures high-quality outputs with standardized processes, aiming to reduce errors typically associated with manual operations.
- **Ensure Consistency**: Standardize and automate processes to maintain consistency across documents and datasets, a critical factor for compliance, research integrity, and business reporting.

### Foster Innovation and Collaboration
- **Encourage Exploration**: CELI serves as a platform for users to explore new areas of automation, potentially leading to innovative applications that redefine existing processes.
- **Build a Community**: Cultivate an open-source community around CELI, where members contribute enhancements, share use cases, and support new users in integrating automation into their workflows.

### Support Diverse Applications
- **Versatile Use Cases**: Designed for flexibility, CELI supports a broad spectrum of applications, from document and data management to complex analytics.
- **Customization and Scalability**: Ensure that CELI can be tailored to specific user needs and scaled up to accommodate large-scale projects, making it suitable for both small teams and large enterprises.

## Overview

CELI comprises several modules, each responsible for a distinct part of the document processing workflow:

- **Processor**: Manages and orchestrates the drafting of documents using language models, acting as the core of the CELI system.
- **Monitor**: Observes and evaluates the performance of the ProcessRunner, ensuring quality and efficiency in automated tasks.
- **Tasks**: Each CELI workflow is a user-defined list of tasks that instruct the agent how to run.
- **Tools**: Tools provide mechansims for CELI to interact with the world.  Tools can be customized for the use case.

These components are in the CELI 'celi_framework.core' package

CELI contains experimental versions of several additional tools that can help develop new use cases more quickly and accomplish different tasks:
- **Pre-Processor**: Converts DOCX documents to a clean Markdown format, making them primed for embedding.
- **Embeddor**: Embeds pre-cleaned text data from source documents, preparing it for machine learning models and data analysis.
- **Mapper**: Focuses on pre-computing mappings between document content, enhancing the efficiency of the embedding process.
- **Post-Monitor**: Evaluates the execution of processes, standardizing task labels and analyzing task quality variations.
- **Mechanic**: Fixes issues identified by the post-monitor, ensuring the system adapts and improves over time.

These components are in `celi_framework.experimental`.

Additionally, `celi_framework.examples` contains examples for applying CELI to different use cases.

## Comparison with Agent-Based Frameworks

CELI represents a paradigm shift in automated knowledge work, distinguishing itself from traditional agentic frameworks through its unique approach to task automation and interaction with large language models (LLMs). Below are key differentiators that set CELI apart:

- **Controller-Embedded LLM Interactions:** Unlike conventional frameworks where the controller scripts orchestrate LLM interactions in a reactive manner, CELI embeds the controller logic directly within LLM prompts. This design philosophy allows for a more seamless and integrated process, enabling the LLM to act upon a broader context and undertake complex tasks with greater autonomy.

- **Beyond Conversation-Like Flows:** Traditional agent-based models often mimic conversational exchanges, limiting the scope and efficiency of task execution. CELI, by contrast, utilizes a pseudo-code structure in its prompts, freeing the interaction model from the constraints of conversational flows. This allows for the development of more sophisticated and task-specific applications without the limitations of a dialogue format.

- **Function Calling Capabilities:** CELI extends the LLM's functionality through an innovative use of function calls within the prompts. This approach transforms the LLM into a dynamic entity capable of retrieving necessary data (getters) and saving produced data (setters), effectively bridging the gap between LLM reasoning and practical application needs.

- **Error Handling and Self-Correction:** A standout feature of CELI is its ability to self-correct and adapt in real-time. In the face of errors or incongruencies, CELI autonomously adjusts its approach, ensuring continuous progress without the need for human intervention at every decision point. This resilience makes CELI particularly suited for handling complex documents and datasets with varying formats and structures.

- **Scalability and Flexibility:** Addressing the challenge of processing voluminous documents and intricate data sets, CELI is designed to scale effortlessly. Its architecture supports both granular tasks and expansive projects, accommodating the diverse needs of automated knowledge work.

- **Comparison with Existing Frameworks:** Existing agent-based frameworks like LangChain, Haystack, and Autogen, while powerful, often face limitations in flow flexibility and dependency on predefined paths or human inputs for decision-making. CELI's controller-embedded design and autonomous capabilities represent a significant evolution, offering a more scalable, efficient, and versatile solution for automated knowledge work.

By fundamentally reimagining the interaction between controllers and LLMs, CELI paves the way for transformative solutions in knowledge work automation. Its innovative approach to task automation, combined with the power of LLMs, marks a new frontier in the development of intelligent, autonomous applications tailored to complex workflows and diverse industry requirements.


<!-- end elevator-pitch -->

## Getting started

<!-- start getting-started -->

[Join our Discord server](https://discord.gg/C5SQNdzV) to ask questions or get involved in our project!

To get an idea of what CELI can do, we have prepackaged an example use case.  In this case, we will have CELI write a wiki page on a topic given an example page and a set of references.

### Install CELI

First, install celi using PIP with the following command:

```bash
pip install celi-framework
```

You can also clone the [GitHub repo](https://github.com/x3n0cr4735/celi) and install CELI from source.  See [Running CELI from Source](https://celi.readthedocs.io/en/stable/contributing/running_celi.html) for info on how to do that.

### Set up a mongo DB server to store documents

CELI uses Mongo to cache LLM responses, store documentsm inspect runs.  If you already have a Mongo server running, you can point Celi to it and it will create a new database called 'celi'.  If not, you can quickly spin up a local mongo server using this docker command:

```bash
docker run --name mongodb -p 27017:27017 -d mongo
```

### Configure your environment

The main script for CELI loads some configuration from environment variables.  The [`python-dotenv`](https://pypi.org/project/python-dotenv/) package is used to load these files from a file called `.env` in the current directory.

Create a .env file with an example configuration, copying the file below and substituting in your OpenAI API key.  If you have the repo cloned, you can copy the .env.example file.

```plaintext
    OPENAI_API_KEY=<REPLACE WITH YOUR OPENAI API KEY>
    OUTPUT_DIR=target/celi_output
    DB_URL=mongodb://localhost:27017/
    EXTERNAL_DB=True
    NO_MONITOR=True
    JOB_DESCRIPTION=celi_framework.examples.wikipedia.job_description.job_description
    TOOL_CONFIG_JSON=celi_framework/examples/wikipedia/example_config.json
    PARSER_MODEL_CLASS=llm_core.parsers.OpenAIParser
    PARSER_MODEL_NAME=gpt-3.5-turbo-16k
```

### Run the example use case

Once you have the steps above done, you can test your setup by running:

```bash
python -m celi_framework.main
```

This example use case uses the wikipedia page for Led Zeppelin as the example document, and then creates a new wiki page for the Jonas Brothers based on the references cited from their wikipedia page.  The result will be put in the `target/drafts` directory.

Note that running this takes around 30 minutes (give or take).

<!-- end getting-started -->

## Documentation

Explore the rest of the documentation to learn more about CELI.
* [Getting Started]() - Learn more about the various ways to run CELI.
* [Running CELI](https://celi.readthedocs.io/en/stable/contributing/running_celi.html) - Learn more about the various ways to run CELI.
* [New Use Cases](https://celi.readthedocs.io/en/stable/contributing/new_use_cases.html) - Learn how to apply CELI to your own use case.
* [API Reference](https://celi.readthedocs.io/en/stable/contributing/reference/index.html) - If you are into reading API docs directly.

## Discord Server

[Join our Discord server](https://discord.gg/C5SQNdzV) to discuss the project with users, contributors, and project authors.

## Contributing

If you would like to contribute to the development of CELI, we welcome contributions of all forms.  For more information on contributing, see the [contributor guidelines](https://celi.readthedocs.io/en/stable/contributing/index.html).

## License

CELI is licensed under the MIT License. Feel free to use, modify, and distribute the framework as per the license terms.
