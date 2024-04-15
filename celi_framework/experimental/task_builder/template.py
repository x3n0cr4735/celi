"""
templates.task_builder.config
Configuration for InteractiveDocumentTemplate

This configuration file is crafted to support the `InteractiveDocumentTemplate` class in facilitating an interactive and dynamic document drafting process. It outlines a workflow that actively involves the user in defining their document drafting objectives and dynamically generates a tailored task list based on user input and content analysis. The configuration enables a highly customized document creation experience, ensuring the output closely aligns with the user's intentions and the specific requirements of the document content.

Key Components:
- `role`: Specifies the user's role in an interactive context, emphasizing active participation in defining the drafting objectives.
- `context`: Establishes the theme of "Interactive Data Collection," indicating a focus on user engagement and data-driven task generation for document drafting.
- `task_list`: Enumerates a series of interactive tasks designed to collect user inputs, confirm file placements, assess document content, and refine drafting objectives. Each task is associated with a specific `function_call` that dictates the action to be performed, alongside the required `arguments`.
- `final_output_task`: Identifies the culminating task of the interactive session, which involves reviewing the complete task list generated from the interactive process.
- `include_prerequisites`: Indicates the linear execution of tasks without considering prerequisites, suitable for this interactive and dynamic setup.
- `general_comments` & `user_message`: Provide essential guidance and prompts to the user, ensuring clear communication and facilitating effective interaction throughout the process.

Usage:
This configuration is specifically designed for use with the `InteractiveDocumentTemplate` class from the `templates.task_builder.factory` module. It leverages the class's capabilities to interpret user inputs, analyze document content, and dynamically generate a customized task list for document drafting or analysis.

Example Workflow:
1. The system, through the `InteractiveDocumentTemplate` class, initiates interaction by gathering the user's document objectives.
2. Users confirm the placement of their document files, enabling the system to access and analyze document content.
3. The system assesses the files and samples text data to inform the drafting process further.
4. Based on the sampled text and user inputs, the system proposes a rephrased intent for the user's confirmation, ensuring alignment with the user's goals.
5. A complete list of tasks is generated, outlining a customized approach to achieve the defined document drafting objectives.

This configuration empowers the `InteractiveDocumentTemplate` to create an interactive guide for document drafting, enhancing user engagement and ensuring the drafting process is responsive to the user's specific needs and the document's content requirements.
"""

from celi_framework.core.job_description import JobDescription, Task

# TODO:
#  Have the user define the expected output format, have them give the required input data,
#  and then have tasks generated from that

job_description = JobDescription(
    role="You are tasked with gathering specific information for document drafting.",
    context="Interactive Data Collection",
    task_list=[
        Task(
            task_name="GatherIntent",
            description="Collect the primary objectives of the document from the user.",
            function_call="interactive_input_handler",
            arguments={
                "question": "What are you trying to accomplish with your document(s)?"
            },
        ),
        Task(
            task_name="ConfirmFilesPlacement",
            description="Ask the user to confirm if they have placed the files in the 'input' directory.",
            function_call="interactive_input_handler",
            arguments={
                "question": "Have you placed your files in the 'input' directory? (yes/no)"
            },
        ),
        Task(
            task_name="AssessFilesInDirectory",
            description="Perform an OS operation to assess the files in the input directory.",
            function_call="os_file_info_handler",
            arguments={"directory": "input"},
        ),
        Task(
            task_name="SampleTextData",
            description="Get a random sampling of text data from the documents in the input directory.",
            function_call="document_sampler_handler",
            arguments={"directory": "input", "sample_count": "5"},
        ),
        Task(
            task_name="RephraseIntentBasedOnSamples",
            description="Rephrase the intent of the exercise based on user input and sampled text.",
            function_call="interactive_input_handler",
            arguments={
                "question": "Based on your input and the document samples, we think you want to [rephrased intent]. Does this align with your goals? (yes/no)"
            },
        ),
        Task(
            task_name="GenerateCompleteTaskList",
            description="Generate a complete list of tasks to accomplish the user's goals based on their input, sample text, and response to the rephrased intent.",
            function_call="task_generator_handler",
            arguments={
                "user_intent": "Provided by user in GatherIntent step",
                "document_samples": "Analyzed in SampleTextData step",
                "user_confirmation": "Provided by user in RephraseIntentBasedOnSamples step",
            },
        ),
    ],
    final_output_task="ReviewCompleteTaskList",
    include_prerequisites=False,
    general_comments="Make sure to accurately capture the user's objectives and document content.",
    initial_user_message="Your feedback is crucial for accurately determining the tasks required for your document(s).",
)
