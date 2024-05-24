# TODO: Notes: kept giving me back hypotheticals, and suggested strategies/outlines, until creating task 7
def make_gpt_alone_prompt(current_prompt, example_prompt_response):
    system_message = """
    You are a professional test taker AI agent.

    I am going to give you step by step instructions on how to draft a free response to a test question.

    We will look at a completed example free response test section that is similar to the test to be worked on.
    """

    user_message = f"""
    Prompt of the test question:
    {current_prompt}

    Task 1
    Task_name: Analyze and Understand the Example Response
    Description: Analyze the example prompt and response to develop a preliminary understanding of the expected response structure, argument style, and evidence use.
    Instructions:
        - Examine the example prompt and response to grasp the expected structure, argumentation style, and use of evidence.
        - Determine the scope of the question to ensure comprehensive coverage of all required aspects without digressing into irrelevant areas.
        - Identify and abstract the key strategies and methodologies from the example response that effectively address the prompt.
    Additional Notes: Prepare to develop a response strategy based on these insights.

    Example prompt and response:
    {example_prompt_response}

    Task 2
    Task_name: Develop Response Strategy
    Description: Formulate a detailed response strategy by integrating the insights gained from the analysis of the example prompt and response.
    Instructions:
        - Based on the analyzed strategies and methodologies, draft a preliminary strategy that outlines how these will be applied to effectively address the current question.

    Task 3
    Task_name: Draft a Numbered Response Outline
    Description: Based on the formulated strategy, draft a detailed and numbered outline for the current test question that mirrors the logical flow, clarity, and analytical depth required.
    Instructions:
        - Construct a numbered outline that includes an introduction with a thesis statement, a body section with evidence from provided sources, and a coherent conclusion.
    Example Outline Format: 
        1. Introduction with thesis statement
        2. Body section with evidence points
        3. Conclusion

    Task 4
    Task_name: Iteratively Draft Each Section of the Response
    Description: Using the previously formulated strategy and outline, iteratively draft each section of the test response, ensuring each part reflects the logical flow, clarity, and analytical depth required.
    Instructions:
        - Begin with drafting the introduction section that includes a thesis statement, outlining the main argument.
        - Proceed to draft each body section sequentially, ensuring each part discusses evidence from the provided sources relevant to the thesis, as detailed in the outline.
        - Conclude by drafting the conclusion section, summarizing the arguments and reinforcing the thesis.
        - Ensure each drafted section transitions smoothly into the next, maintaining a coherent flow throughout the document.

    Task 5
    Task_name: Synthesize Sections into a Final Draft
    Description: Use the drafted sections to create a cohesive final draft that flows well and aligns with the expected structure and length of a model response.
    Instructions:
        - Combine the individually drafted sections into a single cohesive document.
        - Ensure that the transition between sections is smooth, maintaining a logical and seamless narrative flow throughout the document.
        - Review the combined draft to ensure that it adheres to the structural expectations set by the model response, both in terms of length and overall organization.
        - Adjust the draft as necessary to ensure that the entire document is coherent, with each part contributing effectively towards supporting the thesis statement.

    Task 6
    Task_name: Final Response Review
    Description: Review the entire document to ensure that it meets the established criteria based on the insights and structure developed in previous tasks and compare it to a similar prompt, answer pair to ensure structural and thematic consistency.
    Instructions:
        - Review each section of the document to ensure that it follows the logical flow and depth as outlined, comparing it with your understanding of similar tasks.
        - Check that the thesis is clearly stated in the introduction and effectively supported throughout the body sections.
        - Verify that the conclusion effectively summarizes the arguments and reiterates the thesis.
        - Ensure that each section transitions smoothly into the next, maintaining a coherent narrative flow.
        - Assess the use of evidence throughout the document to ensure it is pertinent and effectively integrated into the argument.
    
    """
    return system_message, user_message


def make_gpt_alone_prompt_7_steps(current_prompt, example_prompt_response):
    system_message = """
    You are a professional test taker AI agent.

    I am going to give you step by step instructions on how to draft a free response to a test question.

    We will look at a completed example free response test section that is similar to the test to be worked on.
    """

    user_message = f"""
    Prompt of the test question:
    {current_prompt}

    Task 1
    Task_name: Analyze and Understand the Example Response
    Description: Analyze the example prompt and response to develop a preliminary understanding of the expected response structure, argument style, and evidence use.
    Instructions:
        - Examine the example prompt and response to grasp the expected structure, argumentation style, and use of evidence.
        - Determine the scope of the question to ensure comprehensive coverage of all required aspects without digressing into irrelevant areas.
        - Identify and abstract the key strategies and methodologies from the example response that effectively address the prompt.
    Additional Notes: Prepare to develop a response strategy based on these insights.

    Example prompt and response:
    {example_prompt_response}

    Task 2
    Task_name: Develop Response Strategy
    Description: Formulate a detailed response strategy by integrating the insights gained from the analysis of the example prompt and response.
    Instructions:
        - Based on the analyzed strategies and methodologies, draft a preliminary strategy that outlines how these will be applied to effectively address the current question.

    Task 3
    Task_name: Draft a Numbered Response Outline
    Description: Based on the formulated strategy, draft a detailed and numbered outline for the current test question that mirrors the logical flow, clarity, and analytical depth required.
    Instructions:
        - Construct a numbered outline that includes an introduction with a thesis statement, a body section with evidence from provided sources, and a coherent conclusion.
    Example Outline Format: 
        1. Introduction with thesis statement
        2. Body section with evidence points
        3. Conclusion

    Task 4
    Task_name: Iteratively Draft Each Section of the Response
    Description: Using the previously formulated strategy and outline, iteratively draft each section of the test response, ensuring each part reflects the logical flow, clarity, and analytical depth required.
    Instructions:
        - Begin with drafting the introduction section that includes a thesis statement, outlining the main argument.
        - Proceed to draft each body section sequentially, ensuring each part discusses evidence from the provided sources relevant to the thesis, as detailed in the outline.
        - Conclude by drafting the conclusion section, summarizing the arguments and reinforcing the thesis.
        - Ensure each drafted section transitions smoothly into the next, maintaining a coherent flow throughout the document.

    Task 5
    Task_name: Synthesize Sections into a Final Draft
    Description: Use the drafted sections to create a cohesive final draft that flows well and aligns with the expected structure and length of a model response.
    Instructions:
        - Combine the individually drafted sections into a single cohesive document.
        - Ensure that the transition between sections is smooth, maintaining a logical and seamless narrative flow throughout the document.
        - Review the combined draft to ensure that it adheres to the structural expectations set by the model response, both in terms of length and overall organization.
        - Adjust the draft as necessary to ensure that the entire document is coherent, with each part contributing effectively towards supporting the thesis statement.

    Task 6
    Task_name: Final Response Review
    Description: Review the entire document to ensure that it meets the established criteria based on the insights and structure developed in previous tasks and compare it to a similar prompt, answer pair to ensure structural and thematic consistency.
    Instructions:
        - Review each section of the document to ensure that it follows the logical flow and depth as outlined, comparing it with your understanding of similar tasks.
        - Check that the thesis is clearly stated in the introduction and effectively supported throughout the body sections.
        - Verify that the conclusion effectively summarizes the arguments and reiterates the thesis.
        - Ensure that each section transitions smoothly into the next, maintaining a coherent narrative flow.
        - Assess the use of evidence throughout the document to ensure it is pertinent and effectively integrated into the argument.

    Task 7
    Task_name: Final Draft
    Instructions:
    - Take the outline and review, and create a unified, cohesive, essay that is similar to the format of the example response.

    DRAFT RESPONSE HERE:

    """
    return system_message, user_message


def make_gpt_alone_prompt_simplified(current_prompt, example_prompt_response):
    system_message = """
    You are a professional test taker AI agent. I am going to guide you through the process of drafting a free response to a test question. First, we'll analyze a completed example response to understand the expected structure and argument style.
    """

    user_message = f"""
    **Test Question Prompt:**
    {current_prompt}

    **Analyze and Understand the Example Response**
    - **Task:** Examine the example to understand the expected structure, argumentation style, and evidence use.
    - **Goal:** Develop a response strategy that effectively addresses the current question.

    **Example Response:**
    {example_prompt_response}

    **Develop and Draft Your Response**
    - **Outline Drafting:** Create a brief outline based on the insights from the example.

    - **Response Drafting:** Using the outline, draft each section.

    - **Finalize the Draft:** Review your draft to ensure it is coherent and aligns with the example's structure and depth. Adjust as necessary for clarity and flow.

    **Draft Response Here:**

    """
    return system_message, user_message

# def make_gpt_alone_prompt(current_prompt, example_prompt_response):
#     system_message = f"""
#     You are a professional test taker AI agent.
#
#     I am going to give you step by step instructions on how to draft a free response to a test question.
#
#     We will look at a completed example free response test section that is similar to the test to be worked on.
#     """
#
#     user_message = f"""
#     Prompt of the current test question:
#     {current_prompt}
#
#     Task 1
#     Task_name: Analyze and Understand the Example Response
#     Details: {{'description': 'Analyze the example prompt and response below to develop a preliminary understanding of the expected response structure, argument style, and evidence use.', 'instructions': ['Examine the example prompt and response to grasp the expected structure, argumentation style, and use of evidence.', 'Determine the scope of the question to ensure comprehensive coverage of all required aspects without digressing into irrelevant areas.', 'Identify and abstract the key strategies and methodologies from the example response that effectively address the prompt.'], 'additional_notes': ['Prepare to develop a response strategy based on these insights.']}}
#
#     Example prompt and response:
#     {example_prompt_response}
#
#     Task 2
#     Task_name: Develop response strategy
#     Details: {{'description': 'Formulate a detailed response strategy by integrating the insights gained from the analysis of the example prompt and response.', 'instructions': ['Based on the analyzed strategies and methodologies, draft a preliminary strategy that outlines how these will be applied to effectively address the current question.']}}
#
#     Task 3
#     Task_name: Draft a Numbered Response Outline
#     Details: {{'description': 'Based on the formulated strategy, draft a detailed and numbered outline for the current test question that mirrors the logical flow, clarity, and analytical depth required.', 'instructions': ['Construct a numbered outline that includes an introduction with a thesis statement, a body section with evidence from provided sources (provided in 'Prompt of the current test question'), and a coherent conclusion.'], 'example': {{'Example Outline Format': '1. Introduction with thesis statement\\n2. Body section with evidence points\\n3. Conclusion'}}}}
#
#     Task 4
#     Task_name: Iteratively Draft Each Section of the Response
#     Details: {{'description': 'Using the previously formulated strategy and outline, iteratively draft each section of the test response, ensuring each part reflects the logical flow, clarity, and analytical depth required.', 'instructions': ['Begin with drafting the introduction section that includes a thesis statement, outlining the main argument.', 'Proceed to draft each body section sequentially, ensuring each part discusses evidence from the provided sources relevant to the thesis, as detailed in the outline.', 'Conclude by drafting the conclusion section, summarizing the arguments and reinforcing the thesis.', 'Ensure each drafted section transitions smoothly into the next, maintaining a coherent flow throughout the document.']}}
#
#     Task 5
#     Task_name: Synthesize Sections into a Final Draft
#     Details: {{'description': 'Use the drafted sections to create a cohesive final draft that flows well and aligns with the expected structure and length of a model response.', 'instructions': ['Combine the individually drafted sections into a single cohesive document.', 'Ensure that the transition between sections is smooth, maintaining a logical and seamless narrative flow throughout the document.', 'Review the combined draft to ensure that it adheres to the structural expectations set by the model response, both in terms of length and overall organization.', 'Adjust the draft as necessary to ensure that the entire document is coherent, with each part contributing effectively towards supporting the thesis statement.']}}
#
#     Task 6
#     Task_name: Final Response Review
#     Details: {{'description': 'Review the entire document to ensure that it meets the established criteria based on the insights and structure developed in previous tasks and compare it to a similar prompt, answer pair to ensure structural and thematic consistency.', 'instructions': ["Use the 'retrieve_instructions' function to fetch a prompt and answer pair for a similar question to ensure alignment with standard response formats and expectations.", 'Review each section of the document to ensure that it follows the logical flow and depth as outlined, comparing it with the retrieved example where necessary.', 'Check that the thesis is clearly stated in the introduction and effectively supported throughout the body sections.', 'Verify that the conclusion effectively summarizes the arguments and reiterates the thesis.', 'Ensure that each section transitions smoothly into the next, maintaining a coherent narrative flow.', 'Assess the use of evidence throughout the document to ensure it is pertinent and effectively integrated into the argument.']}}
#     """
#     return system_message, user_message
