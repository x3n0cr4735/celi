# Running CELI

CELI can be run from the command line, with configuration arguments, or directly from code.

## Running from the command line

When running CELI from the command line, all arguments can be passed on the command line, provided in environment variables, or provided in a .env file in the current directory, which will get read in as environment variables.  The precedence is that command line arguments override environment variables, which override valies provided in a .env file.

When running from the command line, you need to include your JobDescription and ToolImplementations classes in the python path.  Two configuration variables control how the job is specified.
   * JOB_DESCRIPTION - This is the name of the class that contains the JobDescription.  This class must have a no-arg constructor.  For the example use case, we use "celi_framework.examples.wikipedia.job_description.job_description"
   * TOOL_CONFIG_JSON - This is the path to a JSON file.  This JSON file will be used to construct the `ToolImplementations` class.  The JSON file will be read in and converted to a dictionary.  This dictionary will then be passed as keyword arguments to the `ToolImplementations` class.

For the example use case, the `WikipediaToolImplementations` is a dataclass that takes 3 arguments (2 are required):


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
   poetry install
   ```

   This command will create a virtual environment and set up all the dependencies for you, allowing you to work on the project in an isolated environment.

5. **Activate the Poetry Environment**

   You can activate the virtual environment created by Poetry to start working on the project:

   ```bash
   poetry shell
   ```

   From here, you can use the command line to run scripts or commands, or configure your IDE to use the virtual environment for development.


