<!-- start elevator-pitch -->
# CELI: Controller-Embedded Language Interactions

**CELI (pronounced 'Kelly')** is a framework designed for the automation of a diverse array of knowledge work tasks. Leveraging the analytical and computational capabilities of large language models (LLMs), CELI facilitates:

- **Autonomous Operation:** Unlike traditional agent-based frameworks, CELI embeds controller logic directly within LLM prompts. This unique approach enables CELI to operate autonomously, adjusting its strategies in real-time to handle errors, incongruencies, and multi-step decision-making without requiring human intervention. CELI's ability to self-correct and adapt ensures continuous progress and efficiency in automated tasks, making it exceptionally suited for complex applications.

- **Flexible Task Automation:** Enables automation across a broad spectrum of tasks, including but not limited to drafting complex documents, conducting systematic literature reviews, data analysis and summarization, and much more.

- **Scalability:** Designed to accommodate projects of any scale, CELI efficiently processes massive datasets and documents, and produces output of any size, making it an ideal solution for both targeted tasks and large-scale knowledge work automation.

- **Streamlined Document Lifecycle Management:** CELI optimizes the entire lifecycle of document processing, encompassing pre-processing, embedding, synthesis, content generation, and quality monitoring.

- **Development Flexibility:** CELI is architecturally designed to support developers in creating bespoke applications that conform to specific industry standards, including compliance, methodological rigor, and auditing requirements. This fosters innovation in the field of automated knowledge work by providing a scalable framework that integrates seamlessly into enterprise ecosystems.

[Join our Discord server](https://discord.gg/C5SQNdzV) to ask questions or get involved in our project!

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

[Join our Discord server](https://discord.gg/C5SQNdzV) to ask questions or get involved in our project!

To get an idea of what CELI can do, we have prepackaged an example use case.  In this case, we will have CELI write a wiki page on a topic given an example page and a set of references.

### Install CELI

First, install celi using PIP with the following command:

`pip install celi-framework`

You can also clone the repo and install CELI from source.  See [Running CELI from Source](#running-celi-from-source) below to get the latest code (recommended).

### Set up a mongo DB server to store documents

CELI uses Mongo to cache LLM responses, store documentsm inspect runs.  If you already have a Mongo server running, you can point Celi to it and it will create a new database called 'celi'.  If not, you can quickly spin up a local mongo server using this docker command:

`docker run --name mongodb -p 27017:27017 -d mongo`

### Configure your environment

The main script for CELI loads some configuration from environment variables.  The [`python-dotenv`](https://pypi.org/project/python-dotenv/) package is used to load these files from a file called `.env` in the current directory.

Create a .env file with an example configuration, copying the file below and substituting in your OpenAI API key.  If you have the repo cloned, you can copy the .env.example file.

    OPENAI_API_KEY=<REPLACE WITH YOUR OPENAI API KEY>
    OUTPUT_DIR=target/celi_output
    DB_URL=mongodb://localhost:27017/
    EXTERNAL_DB=True
    NO_MONITOR=True
    JOB_DESCRIPTION=celi_framework.examples.wikipedia.job_description.job_description
    TOOL_CONFIG_JSON=celi-framework/examples/wikipedia/example_config.json
    PARSER_MODEL_CLASS=llm_core.parsers.OpenAIParser
    PARSER_MODEL_NAME=gpt-3.5-turbo-16k

### Run the example use case

Once you have the steps above done, you can test your setup by running

`python -m celi_framework.main`

This example use case uses the wikipedia page for Led Zeppelin as the example document, and then creates a new wiki page for the Jonas Brothers based on the references cited from their wikipedia page.  The result will be put in the `target/drafts` directory.

Note that running this takes around 30 minutes (give or take).

## Defining a use case for CELI

CELI is an agent framework designed to carry out a series of tasks on a set of documents or document sections.  When CELI executes, it can use tools to accomplish those tasks.  When you configure a new use case for CELI, you define what the tasks are, what the documents or document sections to be worked on are, and provide a set of tools.  Once you specify these things, CELI works to automatically complete these tasks.

### The Wikipedia example use case

We have put in an example use case for celi_framework.  In this use case, we perform one-shot document generation.  We use a single wikipedia page as an example.  We then select a second wikipedia page from a different topic in the same category (bands, drugs, coutnries, etc), to use as the target.  We take only the references, not the content, from the target page and use that along with our example page to generate a new version of the target page.  This use case allows for a natural evaluation as we have the actual version of the target page to compare against for evaluation.

We provide an example script with evaluation that generates several pages from each of 3 categories, and uses BertScore to compare the generated wiki page to the original to judge quality.  To run this eval, run

`python -m celi_framework.examples.wikipedia.eval.run_eval`

We will use the Wikipedia use case to describe the overall process of configuring CELI for a new use case.

### The CELI Job Description

The overall use case is defined in the CELI Job Description object.  When you run CELI, you pass general configuration parameters and a Job Description to the main CELI processor.  The `JobDescription` defines the tasks to be accomplished and the tools to be run.  See (job_description.py)[celi-framework/core/job_description.py] for full details

The job description contains several prompt strings which describe the overall job to be run at a high level along with any general guidance for the agent.  It also contains a `task_list` and a `tool_implementations_class`.

The `task_list` is a list of `Task` objects.  When completing a job, the agent will tackle each task in this list in order.  Each task has a name and a set of details.  The details is a dictionary that will be passed directly to the LLM to describing how to accomplish the task.  

The `tool_implementations_class` is a reference to a class that derives from `ToolImplementations` and contains the tools that the LLM can use to accomplish the task.  This class is described in the next section.

### CELI Tool Implementations

Each public function in the class becomes a tool that the LLM can use.  

There is one required function, `def get_schema(self) -> Dict[str, str]`.  This function returns a dictionary describing the document sections.  The processor will work through the sections, completing the defined tasks for each section.  Each dictionary can have any string values, but it is intended to be a section number followed by a section name.

In addition to the `get_schema` function, the ToolImplementations class can have whatever other functions it needs to enable celi_framework.  Each function should be documented with type hints and a doc string.  The top section of the docstring will be included as the description of the overall function.  If the function takes arguments, there should be a section called "Args:" that contains a list of the arguments to the function and descriptions of each.  An example docstring is given below:

        """
        Extracts text from specified sections of documents.
        It handles different document types and logs any errors or warnings encountered.
        Returns concatenated text from the specified sections of the documents.
        If there is no content for the section, <empty section> will be returned.

        If the response contains "Error:", then there was a problem with the function call.

        Args:
            sections_dict_str (str): A JSON string mapping document names to their respective section numbers.  The json string will have the documents and sections in a dictionary.  The sections values should correspond to an entry in the table of contents for the specified document.
        """


## Running CELI

CELI can be run from the command line, with configuration arguments, or directly from code.

### Running from the command line

When running CELI from the command line, all arguments can be passed on the command line, provided in environment variables, or provided in a .env file in the current directory, which will get read in as environment variables.  The precedence is that command line arguments override environment variables, which override valies provided in a .env file.

When running from the command line, you need to include your JobDescription and ToolImplementations classes in the python path.  Two configuration variables control how the job is specified.
   * JOB_DESCRIPTION - This is the name of the class that contains the JobDescription.  This class must have a no-arg constructor.  For the example use case, we use "celi_framework.examples.wikipedia.job_description.job_description"
   * TOOL_CONFIG_JSON - This is the path to a JSON file.  This JSON file will be used to construct the `ToolImplementations` class.  The JSON file will be read in and converted to a dictionary.  This dictionary will then be passed as keyword arguments to the `ToolImplementations` class.

For the example use case, the `WikipediaToolImplementations` is a dataclass that takes 3 arguments (2 are required):

    @dataclass
    class WikipediaToolImplementations(ToolImplementations):
        example_url: str
        target_url: str
        ignore_updates: bool = False

The example JSON config file we use is:
    {
        "example_url": "https://en.wikipedia.org/wiki/Led_Zeppelin",
        "target_url": "https://en.wikipedia.org/wiki/Jonas_Brothers",
        "ignore_updates": true
    }

When CELI is started from the command line, to reads the JSON config file and calls `WikipediaToolImplmentations` with the 3 arguments.

### Running from code

CELI can also be run from code in addition to the command-line.  Any example of running from code can be seen in the celi-framework/examples/wikipedia/eval/run_eval.py script.  This script iterates through several test sets containing source and target wikipedia URLs.  For each, it runs CELI to generate a document, and then uses [BertScore](https://arxiv.org/abs/1904.09675) to compare the generated document to the actual target wikipedia page.  It prints out a matrix of overall results when it completes.

To run from code, you call `run_celi` passing in `CELIConfig` object.
    from celi_framework.core.runner import CELIConfig, run_celi
    run_celi(CELIConfig(...))

The `CELIConfig` object contains the instance of `JobDescripion` and `ToolImplementations` needed to run CELI as well as some other configuration parameters required.

## Running CELI from Source

If you are interested in modifying or contributiling to CELI, you can install and run it from source.  CELI uses [Poetry](https://python-poetry.org/) to manage dependencies and publishing.

1. If you don't have poetry installed already, install it using the [official installer](https://python-poetry.org/docs/#installing-with-the-official-installer).
2. Clone this repo.
3. Go the the root of the project and run `poetry install`.  This will create a virtual environment and set up all the dependencies for you.
4. From there you can use `poetry shell` to get a command line, or use a poetry plugin for your IDE to pick up dependencies.

## Contributing

We would like folks to create their own projects with the framework to address their own use cases. Please feel free to do so! [Join our Discord server](https://discord.gg/C5SQNdzV) if you have questions about contributing.

## License

CELI is licensed under the MIT License. Feel free to use, modify, and distribute the framework as per the license terms.
