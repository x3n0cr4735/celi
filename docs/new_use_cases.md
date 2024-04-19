# New Use Cases

CELI is an agent framework designed to carry out a series of tasks on a set of documents or document sections.  When CELI executes, it can use tools to accomplish those tasks.  When you configure a new use case for CELI, you define what the tasks are, what the documents or document sections to be worked on are, and provide a set of tools.  Once you specify these things, CELI works to automatically complete these tasks.

## The Wikipedia example use case

We have put in an example use case for celi_framework.  In this use case, we perform one-shot document generation.  We use a single wikipedia page as an example.  We then select a second wikipedia page from a different topic in the same category (bands, drugs, coutnries, etc), to use as the target.  We take only the references, not the content, from the target page and use that along with our example page to generate a new version of the target page.  This use case allows for a natural evaluation as we have the actual version of the target page to compare against for evaluation.

We provide an example script with evaluation that generates several pages from each of 3 categories, and uses BertScore to compare the generated wiki page to the original to judge quality.  To run this eval, run

```python 
python -m celi_framework.examples.wikipedia.eval.run_eval
```

We will use the Wikipedia use case to describe the overall process of configuring CELI for a new use case.

## The CELI Job Description

The overall use case is defined in the CELI Job Description object.  When you run CELI, you pass general configuration parameters and a Job Description to the main CELI processor.  The `JobDescription` defines the tasks to be accomplished and the tools to be run.  See (job_description.py)[celi-framework/core/job_description.py] for full details

The job description contains several prompt strings which describe the overall job to be run at a high level along with any general guidance for the agent.  It also contains a `task_list` and a `tool_implementations_class`.

The `task_list` is a list of `Task` objects.  When completing a job, the agent will tackle each task in this list in order.  Each task has a name and a set of details.  The details is a dictionary that will be passed directly to the LLM to describing how to accomplish the task.  

The `tool_implementations_class` is a reference to a class that derives from `ToolImplementations` and contains the tools that the LLM can use to accomplish the task.  This class is described in the next section.

## CELI Tool Implementations

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


