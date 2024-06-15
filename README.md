[![PyPI version](https://badge.fury.io/py/celi-framework.svg)](https://badge.fury.io/py/celi-framework)
[![Tests](https://github.com/x3n0cr4735/celi/actions/workflows/tests.yml/badge.svg)](https://github.com/x3n0cr4735/celi/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/celi/badge/?version=latest)](https://celi.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Versions](https://img.shields.io/pypi/pyversions/celi-framework)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

![CELI Logo](docs/CELI_README_Header_Picture.png)

 <!-- start elevator-pitch -->
# <b>C</b>ELI: A Framework for <u><b>C</b></u>ontroller-<u><b>E</b></u>mbedded <u><b>L</b></u>anguage <u><b>I</b></u>nteractions

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

CELI (Controller-Embedded Language Interactions) automates projects by decomposing them into sets of tasks and utilizing LLM-directed controller logic for execution. Key features include:

- ### 💡 **Inversion of Control and Dynamic LLM-OOP Integration**

  - Transforms traditional hierarchical models by embedding the LLM controller within the operational fabric of Object-Oriented Programming (OOP) via Inversion of Control (IoC).
  - This integration moves away from a single OOP controller directing multiple LLM agents and instead allows the LLM controller to actively manage and execute OOP functions. 
  - Each OOP function directly interacts with the LLM controller, enhancing their autonomy and enabling dynamic function calls. 
  - This setup ensures cohesive system operation and facilitates real-time interactions with external systems like APIs, databases, and LLM agents, significantly boosting flexibility and enabling complex operations.

- ### 🔄 **Dynamic Workflow Management**

    Supports complex workflows with the capability for nested operations and recursion within tasks. This dynamic structure allows workflows to adapt based on contextual changes or external data inputs, providing unparalleled flexibility and responsiveness.

- ### ⚙️ **Automation Engine**

    Acts as the central orchestrating unit, managing all operations from data handling to task execution. The engine efficiently handles both predefined tasks and dynamic adjustments, ensuring seamless automation across diverse platforms and use cases.

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

You can also clone the [GitHub repo](https://github.com/x3n0cr4735/celi) and install CELI from source.  See [Running CELI from Source](https://celi.readthedocs.io/en/stable/running_celi.html) for info on how to do that.


### Run the example use case

Once you have the steps above done, you can test your setup by running a demo of CELI's capabilities:

```bash
python -m celi_framework.main \
  --job-description=celi_framework.examples.human_eval.job_description.job_description \
  --tool-config='{"single_example":"HumanEval/3"}' \
  --simulate-live
```

This example simulates using CELI to solve problem #3 of the HumanEval benchmark programming problem set.  It uses 
cached versions of the LLM outputs so it doesn't require an API key or make any paid LLM calls on your behalf.  The 
result will be put in the `target/drafts` directory.

Running this demo should take a couple minutes.  You will be able to see how CELI tackles the problem and the LLM calls
it makes, along with the responses.

### Running live

The code above uses a cached version of the LLM results.  To meaningfully run CELI on anything new, you will need to 
make new LLM calls, which will require an OpenAI API key (or your own local LLM.  See [LLM Support](https://celi.readthedocs.io/en/stable/llm_support.html)).

We can now run the full HumanEval data set.  This has 168 examples, so we won't use --simulate-live to impose a delay.

```bash
python -m celi_framework.main \
  --job-description=celi_framework.examples.human_eval.job_description.job_description \
  --openai-api-key=<Insert your OpenAI API key here> \
```

You can also set an OPENAI_API_KEY environment variable instead of passing one on the command line.

<!-- end getting-started -->

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