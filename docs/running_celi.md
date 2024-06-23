# Running CELI

CELI can be run from the command line, with configuration arguments, or directly from code.

## Running from the command line

When running CELI from the command line, all arguments can be passed on the command line, provided in environment variables, or provided in a .env file in the current directory, which will get read in as environment variables.  The precedence is that command line arguments override environment variables, which override values provided in a .env file.

Full instructions on running CELI from the command line are available in with the -h flag:

```
usage: main.py [-h] [--openai-api-key OPENAI_API_KEY] [--primary-model-name PRIMARY_MODEL_NAME]
               [--max-tokens MAX_TOKENS] [--model-api-url MODEL_API_URL] [--job-description JOB_DESCRIPTION]
               [--simulate-live] [--no-cache] [--tool-config-json TOOL_CONFIG_JSON] [--tool-config TOOL_CONFIG]

All of the options below can also be set as environment variables(using the capitalized names), or in a local .env
file.

options:
  -h, --help            show this help message and exit
  --openai-api-key OPENAI_API_KEY
                        Your OpenAI API key. For security reasons, it is preferrable to set this as an environment
                        variable rather than passing it on the command line. If you are serving your own models using
                        --model-api-url, this will be the API keypassed in the calls to those models. The specific
                        value required will depend on the server.
  --primary-model-name PRIMARY_MODEL_NAME
                        Name of the primary LLM to use. This will be passed in the OpenAI LLM calls. If you are using
                        OpenAI, you can use any of the OpenAI model names found at
                        https://platform.openai.com/docs/models. If you areserving your own models (using --model-api-
                        url), you can use any name that the server supports.
  --max-tokens MAX_TOKENS
                        The maximum number of tokens to be included in any one request. This is a comprehensive
                        number, it includes the tokens in the system message, chat history, and output response.
                        Setting this to a largernumber than the default 4096 increases cost but allows for longer
                        prompts and responses. You may need toset this shorter if you are using a non-OpenAI model
                        with a shorter context length.
  --model-api-url MODEL_API_URL
                        Sets the URL to use when making OpenAI LLM calls. Leave this blank to use the normal OpenAI
                        models. Ifyou are serving models locally using a server that implements the OpenAI API, you
                        can set this to the URL for that server. Several serving platforms support the OpenAI
                        interface, including vLLM, NIMs, Ollama.
  --job-description JOB_DESCRIPTION
                        CELI requires a job description to know what task to run. This parameter specifies the Python
                        class name for the class containing the job description. It must have JobDescription as a base
                        class. Several example job descriptions are provided within the celi_framework.examples
                        module.
  --token_budget TOKEN_BUDGET
                        Total budget in tokens for a singe CELI run, across all calls. If set to 0, there is no
                        budget. This only includes live calls, not cached calls. If the budget is exceeded, the run
                        will stop.
  --simulate-live       Set to true to add a delay to the LLM cache. This simulates what a live run would look like
                        even when cached LLM results are used
  --no-cache            Set to True to turn off LLM caching
  --tool-config-json TOOL_CONFIG_JSON
                        Path to a JSON file which will be used to configure the tools. See --tool-config for more
                        information.This option allows the JSON to be specified in a file instead of the command line.
                        If --tool-config isalso specified, this option will be ignored.
  --tool-config TOOL_CONFIG
                        This should be a JSON string which will be used to configure the tools. The JSON will be
                        converted into an object, which will be passed as keyword arguments to the tool
                        implementation. The specific values required (if any) will depend on the tool implementations.
                        For the HumanEval tools, a single argument can be passed that indicates only one example
                        should be run. --tool-config='{"single_example":"HumanEval/3"}' This option overrides --tool-
                        config-json if both are set.
```

## Environment variables

All command line options can optionally be specified as environment variables.  Use the capitalized version shown in the help message above.

Additionally, the [`python-dotenv`](https://pypi.org/project/python-dotenv/) package is used to load a file called `.env` in the current directory and set it's
values.  This allows you to have a simple file where all options are stored.

To create a .env file with an example configuration, copying the file below and substituting in your OpenAI API key.  If you have the repo cloned, you can copy the .env.example file.

```
OPENAI_API_KEY=sk-XXXX
NO_CACHE=False
JOB_DESCRIPTION=celi_framework.examples.wikipedia.job_description.job_description
TOOL_CONFIG_JSON=celi_framework/examples/wikipedia/example_config.json
```

## Tool Configurations

For the wikipedia example use case, the `WikipediaToolImplementations` is a dataclass that takes 3 arguments (2 are required):


```python
@dataclass
class WikipediaToolImplementations(ToolImplementations):
    example_url: str
    target_url: str
    ignore_updates: bool = False
```

The example JSON config file we use is:

```json
{
    "example_url": "https://en.wikipedia.org/wiki/Led_Zeppelin",
    "target_url": "https://en.wikipedia.org/wiki/Jonas_Brothers",
    "ignore_updates": true
}
```

When CELI is started from the command line, to reads the JSON config file and calls `WikipediaToolImplmentations` with the 3 arguments.

## Optional packages

The core CELI framework is installed using PIP.  There are also certain optional dependencies that can be installed to
add additional functionality.  To install these, run:

```
pip install celi-framework[wikipedia,experimental]
``` 

Note these dependencies may require certain system packages to be installed and may require several gigs of disk space.

## Calling CELI from Python

CELI can also be embedded in an existing Python program in addition to the command-line.  Any example of running from code can be seen in the celi-framework/examples/wikipedia/eval/run_eval.py script.  This script iterates through several test sets containing source and target wikipedia URLs.  For each, it runs CELI to generate a document, and then uses [BertScore](https://arxiv.org/abs/1904.09675) to compare the generated document to the actual target wikipedia page.  It prints out a matrix of overall results when it completes.

To run from code, you call `run_celi` passing in `CELIConfig` object:

```python
    from celi_framework.core.runner import CELIConfig, run_celi
    run_celi(CELIConfig(...))
```

The `CELIConfig` object contains the instance of `JobDescripion` and `ToolImplementations` needed to run CELI as well as some other configuration parameters required.

# Running CELI from Source

If you are interested in modifying or contributiling to CELI, you can install and run it from source.  CELI uses [Poetry](https://python-poetry.org/) to manage dependencies and publishing. That being said, there are two recommended methods:

## Anaconda

1. Install Anaconda

Download and install Anaconda from the [official Anaconda distribution page](https://www.anaconda.com/products/distribution). Follow the installation instructions suitable for your operating system.

2. Create an Anaconda Environment

Open your terminal or Anaconda Prompt and create a new Conda environment using Python 3.11:

```bash
conda create -n celi_env python=3.11
conda activate celi_env
```

This sets up a clean environment specifically for running CELI, avoiding conflicts with other projects or system-wide Python packages.

3. Clone the Repository

Clone the CELI repository from GitHub to your local machine:

```bash
git clone https://github.com/x3n0cr4735/celi.git
```

4. Change to the Directory with the Repository

Navigate to the directory where the repository has been cloned:

```bash
cd celi
```

5. Install the Project Using pip

While inside the project directory and with your Conda environment activated, install the project and its dependencies in editable mode:

```bash
pip install -e .
```

This command will install all necessary dependencies as specified in the project's `setup.py` or `pyproject.toml` and will allow you to modify the project and have the changes reflected immediately. 


## Poetry

1. **Install Poetry**

   Download and install Poetry using the [official installer](https://python-poetry.org/docs/#installing-with-the-official-installer). Follow the instructions on the page to download and install Poetry for your operating system.

2. **Clone the Repository**

   Clone the CELI repository from GitHub to your local machine:

   ```bash
   git clone https://github.com/x3n0cr4735/celi.git
   ```

3. **Change to the Directory with the Repository**

   Navigate to the directory where the repository has been cloned:

   ```bash
   cd celi
   ```

4. **Install the Project Using Poetry**

   While inside the project directory, install the project and its dependencies using Poetry:

   ```bash
   poetry install --all-extras
   ```

   This command will create a virtual environment and set up all the dependencies for you, allowing you to work on the project in an isolated environment.

5. **Activate the Poetry Environment**

   You can activate the virtual environment created by Poetry to start working on the project:

   ```bash
   poetry shell
   ```

   From here, you can use the command line to run scripts or commands, or configure your IDE to use the virtual environment for development.


