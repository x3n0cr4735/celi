def make_gpt_prompt(current_prompt, example_prompt_response):
    """
    Function to guide the creation of a GPT prompt using a structured approach defined by a series of tasks.

    Args:
    current_prompt (str): The current test question prompt.
    example_prompt_response (str): An example prompt and its response for analysis.

    Returns:
    Tuple[str, str]: A tuple containing system and user messages.
    """

    system_message = """
    You are a professional AI test taker.

    I am going to guide you step by step on how to draft a free response to a test question.

    We will look at a completed example free response test section that is similar to the test to be worked on.
    """

    user_message = f"""
    Prompt of the test question:
    {current_prompt}

    Task 1
    Task_name: Analyze and Understand the Example Prompt & Response
    Description: Analyze the example prompt and response to develop a preliminary understanding of the expected response structure, argument style, and evidence use.
    Instructions:
        - Examine the example prompt and response to grasp the expected structure, argumentation style, and use of evidence.
        - Identify and abstract the key strategies and methodologies from the example response that effectively address the prompt.
    Additional Notes: Prepare to develop a response strategy based on these insights.
    Prompt and response for example question:
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
    Task_name: Synthesize Sections into a Draft
    Description: After drafting individual sections, this task involves combining them into a single, cohesive final draft. The objective is to ensure that the document flows logically from introduction to conclusion, maintaining a unified argument that effectively addresses the prompt.
    Instructions:
        - Combine the drafted sections starting with the introduction, followed by the body sections, and ending with the conclusion.
        - Ensure that transitions between sections are smooth and logical, enhancing the overall flow and readability of the document.
        - Check that the final draft maintains a consistent style, tone, and voice throughout, which are important for presenting a professional and coherent argument.
        - Review the entire document to ensure that it aligns with the response strategy and meets the structural and content expectations outlined previously.

    Task 6
    Task_name: Review Draft
    Description: This final review task is crucial for ensuring that the complete document meets the established criteria, drawing on insights and structures developed in previous tasks.
    Instructions:
        - Use the 'retrieve_instructions' function to fetch a prompt and answer pair for a similar question, ensuring alignment with standard response formats and expectations.
        - Review each section of the document to confirm it follows the logical flow and depth outlined, comparing it with the retrieved example where necessary.
        - Check that the thesis is clearly stated in the introduction and is effectively supported throughout the body sections.
        - Verify that the conclusion effectively summarizes the arguments and reinforces the thesis.
        - Ensure that each section transitions smoothly into the next, maintaining a coherent narrative flow.
        - Assess the use of evidence to ensure it is pertinent and effectively integrated into the argument.

    Task 7
    Task_name: Recommend Revisions with Review Output
    Description: This task involves identifying necessary revisions based on detailed feedback and assessments provided in the 'Draft Review' task. The goal is to pinpoint areas where the document can be improved to meet established criteria, thus enhancing clarity, coherence, and argumentative strength based on the review outputs.
    Instructions:
        - Review the feedback provided in the 'Section Review', 'Draft Quality', and 'Final Verdict' components from the Draft Review.
        - Identify key areas requiring improvement—these may include areas where argumentation needs to be strengthened, the thesis needs to be clearer, transitions between sections need to be smoother, or grammatical and formatting errors need to be corrected.
        - Recommend specific revisions for each section of the document, focusing on the areas highlighted in the feedback.
        - Suggest re-evaluation of the evidence used in the response to ensure it aligns well with the thesis and supports the overall argument effectively.
        - Propose how to ensure that all recommended revisions will maintain the logical flow and coherence of the response, thus enhancing its overall persuasive impact.

    Task 8
    Task_name: Redraft
    Description: Redraft with recommended revisions.
    Instructions:
        - Revise each of the sections and subsections drafted separately in 'Iteratively Draft Each Section of the Response'.
        - Execute these revisions as sub-tasks, ensuring each section and sub-section is handled one at a time to maintain focus and precision.
        - Make sure to incorporate all recommended revisions to enhance the clarity, coherence, and overall effectiveness of each section.
        - Reassess each redrafted section to ensure that the revisions are appropriately integrated and that the section aligns with the overall strategy and response outline.
    Note:
        - This task needs to be executed as sub-tasks. Draft each section and sub-section separately in sequential prompts/completions (one response at a time).
    Example:
        - Example Revised Section: "Introduction: [Revised draft text of introduction here, incorporating feedback and enhancing clarity and engagement.]" 
    ADDITIONAL COMMENTS:
        - Be very critical during the redrafting process. Try to identify any remaining weaknesses or areas for improvement.
        - Pay special attention to maintaining a logical flow between sections, ensuring that transitions are smooth and support the overall argument.

    DRAFT RESPONSE HERE:
    """
    return system_message, user_message

def make_gpt_prompt_simple(current_prompt, example_prompt_response):
    """
    Guide the creation of a GPT-style prompt by examining the current prompt, analyzing an example,
    formulating a strategy, drafting a detailed outline, and iteratively drafting the response.

    Args:
        current_prompt (str): The current test question prompt.
        example_prompt_response (str): An example prompt and its response for analysis.

    Returns:
        Tuple[str, str]: A tuple containing a system message and a user message.
    """

    system_message = """
    You are a professional AI test taker.

    This process will guide you step by step on how to effectively respond to a GPT-style test question,
    examining a similar example, and developing a strategy for drafting a high-quality response.
    """

    user_message = f"""
    ---------------
    
    Prompt of the test question:
    {current_prompt}
    
    ---------------

    Task 1: Analyze and Understand the Example Question's Prompt & Response
    Description: Critical analysis of an example response to a prompt similar to the one at hand is essential for understanding effective response strategies.
    Instructions:
        - Retrieve an example prompt and response using the provided function call.
        - Examine the structure, argumentation style, and evidence utilization.
        - Identify key argumentation techniques and how evidence is integrated.
        - Abstract effective strategies such as rhetorical devices, logical reasoning, and evidence presentation.
    Additional Notes:
        - Highlight innovative methods and consider the context of their effectiveness.
        
    ------------
        
    Example Question Prompt & Response:
    {example_prompt_response}

    -------------

    Task 2: Develop Response Strategy
    Description: Formulate a comprehensive strategy to address the prompt effectively by integrating key findings from the example analysis.
    Instructions:
        - Synthesize insights into a cohesive strategy document.
        - Develop a structured plan detailing the introduction, arguments, evidence integration, and conclusion.
        - Ensure flexibility to accommodate prompt variations or new insights.
    Additional Notes:
        - Document the strategy clearly for use during drafting and consider peer review to refine it.

    Task 3: Draft a Numbered Response Outline
    Description: Utilizing the developed strategy, draft a detailed outline that maps the response structure.
    Instructions:
        - Start with an introduction that sets the context and states the thesis clearly.
        - List main points for the body, detailing the argument and evidence for each.
        - Conclude with a summary that reinforces the thesis and encapsulates main arguments.
    Example Outline Format:
        1. Introduction with thesis statement
        2. Body section 1 with evidence point
        3. Body section 2 with another evidence point
        4. Conclusion
    Additional Notes:
        - Use the outline as a drafting guide and checklist to ensure coverage of all critical points.

    Task 4: Iteratively Draft Each Section of the Response
    Description: Draft each section as outlined, focusing on articulation, coherence, and supporting the thesis.
    Instructions:
        - Begin with the introduction, clearly stating the thesis and setting the response's tone.
        - Draft each body section, elaborating on points with appropriate evidence.
        - Ensure smooth transitions between sections for a cohesive argument.
        - Conclude with a strong summary that reiterates the thesis.
    Additional Notes:
        - Iterate on drafts to improve clarity, flow, and impact, incorporating feedback as necessary.

    DRAFT RESPONSE HERE:
    """

    return system_message, user_message

def score_llm_prompt(prompt:str, llm_output: str, rubric: str):

    system_message = """
    You are a professional AI test scorer.

    This process will guide you step by step on how to effectively grade to an essay test question.

    Return the same essay as is and the score of the essay at the beginning of the text.
    """

    user_message = f"""
    Grade an essay using the included rubric.

    Take this test question prompt:
    {prompt}
    
    Essay:
    {llm_output}
    
    And score it using this rubric:
    {rubric}

    """
    return system_message, user_message

