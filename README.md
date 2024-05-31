[![PyPI version](https://badge.fury.io/py/celi-framework.svg)](https://badge.fury.io/py/celi-framework)
[![Tests](https://github.com/x3n0cr4735/celi/actions/workflows/tests.yml/badge.svg)](https://github.com/x3n0cr4735/celi/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/celi/badge/?version=latest)](https://celi.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Versions](https://img.shields.io/pypi/pyversions/celi-framework)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

![CELI Logo](docs/CELI_README_Header_Picture.png)

# <b>C</b>ELI: A Framework for <u><b>C</b></u>ontroller-<u><b>E</b></u>mbedded <u><b>L</b></u>anguage Model <u><b>I</b></u>nteractions

**CELI (pronounced 'Kelly')** leverages the capabilities of large language models (LLMs) to automate a wide range of knowledge work tasks. Here’s an overview of what CELI offers:

- 🚀 **Autonomous Operation:** Functions independently, dynamically adapting strategies without human intervention.
- 🛠️ **Flexible Task Automation:** Applicable across diverse tasks from document drafting to data analysis.
- 📈 **Scalability:** Efficiently manages projects of varying sizes and complexities.
- 📊 **Streamlined Document Management:** Enhances every phase of the document lifecycle management.
- 🏗️ **Development Flexibility:** Supports the development of custom applications that meet specific industry standards.

🔗 [Join our Discord](https://discord.gg/C5SQNdzV) | 🔗 [Read our Docs](https://celi.readthedocs.io/en/latest/)

<p>
  <i class="fa fa-exclamation-triangle"></i>
  <strong>Important:</strong> CELI is currently in alpha. For support, join our Discord server or submit an issue on this GitHub repo.
</p>

## What is CELI?

CELI (Controller-Embedded Language Interactions) is a sophisticated framework designed to enhance automation by incorporating advanced components into its architecture. Unlike traditional AI agent frameworks that feature a hierarchical control structure, CELI integrates controller logic directly with operational functions for more dynamic and efficient task management. Key features include:

- ### 💡 **Inversion of Control and Dynamic LLM-OOP Integration**

  - Transforms traditional hierarchical models by embedding the LLM controller within the operational fabric of Object-Oriented Programming (OOP) via Inversion of Control (IoC).
  - This integration moves away from a single OOP controller directing multiple LLM agents and instead allows the LLM controller to actively manage and execute OOP functions. 
  - Each OOP function directly interacts with the LLM controller, enhancing their autonomy and enabling dynamic function calls. 
  - This setup ensures cohesive system operation and facilitates real-time interactions with external systems like APIs, databases, and LLM agents, significantly boosting flexibility and enabling complex operations.

- ### 🔄 **Dynamic Workflow Management**

    Supports complex workflows with the capability for nested operations and recursion within tasks. This dynamic structure allows workflows to adapt based on contextual changes or external data inputs, providing unparalleled flexibility and responsiveness.

- ### ⚙️ **Automation Engine**

    Acts as the central orchestrating unit, managing all operations from data handling to task execution. The engine efficiently handles both predefined tasks and dynamic adjustments, ensuring seamless automation across diverse platforms and use cases.

## Getting started

[Join our Discord server](https://discord.gg/C5SQNdzV) to ask questions or get involved in our project!

To get an idea of what CELI can do, we have prepackaged an example use case.  In this case, we will have CELI write a wiki page on a topic given an example page and a set of references.

### Install CELI

First, install celi using PIP with the following command:

```bash
pip install celi-framework
```

You can also clone the [GitHub repo](https://github.com/x3n0cr4735/celi) and install CELI from source.  See [Running CELI from Source](https://celi.readthedocs.io/en/stable/running_celi.html) for info on how to do that.

### Set up a mongo DB server to store documents

CELI uses Mongo to cache LLM responses, store documentsm inspect runs.  If you already have a Mongo server running, you can point Celi to it and it will create a new database called 'celi'.  If not, you can quickly spin up a local mongo server using this docker command:

```bash
docker run --name mongodb -p 27017:27017 -d mongo
```

### Configure your environment

The main script for CELI loads some configuration from environment variables.  The [`python-dotenv`](https://pypi.org/project/python-dotenv/) package is used to load these files from a file called `.env` in the current directory.

Create a .env file with an example configuration, copying the file below and substituting in your OpenAI API key.  If you have the repo cloned, you can copy the .env.example file.

    OPENAI_API_KEY=<REPLACE WITH YOUR OPENAI API KEY>
    OUTPUT_DIR=target/celi_output
    DB_URL=mongodb://localhost:27017/
    EXTERNAL_DB=True
    NO_MONITOR=True
    JOB_DESCRIPTION=celi_framework.examples.wikipedia.job_description.job_description
    TOOL_CONFIG_JSON=celi_framework/examples/wikipedia/example_config.json
    PARSER_MODEL_CLASS=llm_core.parsers.OpenAIParser
    PARSER_MODEL_NAME=gpt-3.5-turbo-16k

### Run the example use case

Once you have the steps above done, you can test your setup by running:

```bash
python -m celi_framework.main
```

This example use case uses the wikipedia page for Led Zeppelin as the example document, and then creates a new wiki page for the Jonas Brothers based on the references cited from their wikipedia page.  The result will be put in the `target/drafts` directory.

Note that running this takes around 30 minutes (give or take).

## Project Overview

CELI is structured into distinct packages, each housing modules responsible for different aspects of the document processing workflow.

### Core Modules
Located in the `celi_framework.core` package, the following essential core modules facilitate CELI's primary operations:

- **Processor**: Manages and orchestrates the drafting of documents using language models, acting as the core of the CELI system.
- **Monitor**: Observes and evaluates the performance of the ProcessRunner, ensuring quality and efficiency in automated tasks.
- **Job Description**: Manages a comprehensive list of user-defined job descriptions that guide how tasks are executed.
- **Tools**: Provides mechanisms for CELI to interact with external systems and can be customized to suit specific use cases.

### Customizable Extensions
Users extend the CELI framework by defining their own job descriptions and tools, which leverage and extend the functionalities of the core modules. This allows for a high degree of customization and tailoring to specific needs:

- **User-Defined Job Descriptions**: Users can create unique job descriptions that specify detailed instructions and operational steps, ensuring that automated processes align closely with project requirements.
- **Custom Tool Implementations**: Developers can implement custom tools by importing core modules and utilizing their functionalities. These tools can be adapted to integrate seamlessly with existing systems or to introduce new capabilities.

### Experimental Modules
Located in the `celi_framework.experimental` package, these modules are designed to support the development of new use cases and enhance existing functionalities:

- **Pre-Processor**: Converts DOCX documents into a clean Markdown format, priming them for further processing.
- **Embeddor**: Embeds pre-cleaned text data from source documents, preparing it for integration with machine learning models and data analysis.
- **Mapper**: Focuses on pre-computing mappings between document contents to enhance the efficiency of the embedding process.

### Example Use Cases
For practical applications and demonstrations, explore the `celi_framework.examples` package:

- This package contains a variety of examples demonstrating how CELI can be applied across different scenarios and use cases.

## Secret Sauce: Controller-Embedded Recursion

CELI's architecture uniquely integrates recursion within its operational logic, significantly enhanced by embedding controller logic directly within LLM prompts. This sophisticated structure enables CELI to efficiently handle complex, multi-layered tasks with greater autonomy. The key capabilities facilitated by this approach include:

- ### ⚙️ Controller-Embedded Recursion

    Controllers within LLM prompts direct the flow of operations, establishing loops that enable recursion crucial for managing complex sequences, where tasks may depend on the outcomes of preceding actions or require repeated iterations until a certain condition is met.

- ### 🔄 Deep Task Nesting

    CELI manages tasks requiring multiple layers of sub-tasks, recursively processing each layer across various sections of documents or elements within data structures like dictionaries or lists, enhancing the system’s ability to handle diverse and complex workflows.

- ### 🛠️ Sophisticated Error Handling

    By leveraging recursion, CELI dynamically identifies and manages errors or inconsistencies during task execution, ensuring reliability and operational accuracy.

- ### 🧠 Adaptive Learning Loops

    The recursive nature of CELI’s task management supports an environment of adaptive learning, continuously refining strategies and approaches based on ongoing interactions and feedback.

## CELI vs. LLM Agents

CELI offers a distinct approach to automated knowledge work, setting it apart from traditional agent-based frameworks with its effective integration of task automation and interaction with large language models (LLMs). Key differentiators include:

- ### 🎛️ Integrated Control Logic

    CELI’s controller logic embedded within LLM prompts enables a more autonomous and streamlined operation for handling complex tasks, reducing the dependency on manual interventions.

- ### 🏗️ Enhanced Task Structuring

    Unlike traditional models confined to conversational dynamics, CELI employs a structured pseudo-code approach, allowing for complex and precise task execution beyond simple dialogue systems.

- ### 🔁 Recursive Task Management 

    Utilizes recursion to manage multiple layers of tasks efficiently, allowing for dynamic adaptation in response to operational challenges, enhancing system reliability and responsiveness.

- ### 🌐 Active Data Management

    Enhances LLM utility by embedding function calls within operational prompts, enabling real-time data interactions crucial for applying model outputs effectively in real-world scenarios.

- ### 📈 Robust and Adaptable Framework

    Designed to handle a wide range of demands, from small tasks to large-scale projects, CELI’s architecture supports diverse requirements without sacrificing performance.

## Discord Server

[Join our Discord server](https://discord.gg/C5SQNdzV) to discuss the project with users, contributors, and project authors.

## Documentation

Explore the rest of the documentation to learn more about CELI.
* [Getting Started](https://celi.readthedocs.io/en/stable/getting_started.html) - Learn more about the various ways to run CELI.
* [Running CELI](https://celi.readthedocs.io/en/stable/running_celi.html) - Learn more about the various ways to run CELI.
* [New Use Cases](https://celi.readthedocs.io/en/stable/new_use_cases.html) - Learn how to apply CELI to your own use case.
* [API Reference](https://celi.readthedocs.io/en/stable/reference/index.html) - If you are into reading API docs directly.
The CELI dev team is committed to continuous improvement and user-driven development. Whether you're a seasoned developer or just starting, your feedback and contributions are invaluable to us. Let's build a smarter future together!

## Contributing

If you would like to contribute to the development of CELI, we welcome contributions of all forms.  For more information on contributing, see the [contributor guidelines](https://celi.readthedocs.io/en/stable/contributing/index.html).

## License

CELI is licensed under the MIT License. Feel free to use, modify, and distribute the framework as per the license terms.
