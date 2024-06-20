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

def make_gpt_prompt_alpaca(current_instruction, example_instruction_output):
    """
    Guide the creation of a response for the alpaca_eval dataset by examining the current instruction,
    comparing it to an example instruction and its output, and effectively formulating an answer.

    Args:
        current_instruction (str): The current instruction requiring a response.
        example_instruction_output (str): An example instruction paired with its output to aid in understanding response expectations.

    Returns:
        Tuple[str, str]: A tuple containing a system message and a user message.
    """

    system_message = """
    As an AI trained to assist with the answering questions, your goal is to generate concise and precise answers to the provided instructions.
    This guide will help you step by step to formulate responses that are not only correct but also well-informed and contextually relevant.
    """



    initial_User_Message = "Welcome to your task dashboard for the Alpaca_Eval dataset. Please review the question in the dataset and start with the first uncompleted task. Focus on generating accurate and comprehensive responses. Refer to any previous tasks if needed to maintain continuity and accuracy."

    pre_algo_instruct = "Before we start answering questions from the Alpaca_Eval dataset, ensure you understand the context and requirements of each question. You will be provided with the question and expected to research and draft a response based on reliable sources. Pay close attention to the specifics of each question to tailor your responses appropriately."

    post_algo_instruct = "After drafting your response, review it against the example outputs provided for quality and comprehensiveness. Ensure your final response aligns with the expected format and detail as illustrated by successful examples. Reflect on any feedback or revisions suggested in the dataset guidelines to optimize your response before submission."




    user_message = f"""
    ---------------
  
    
    {pre_algo_instruct}
    
    ---------------

    Analyze the Example Instruction and Output:
    Analyse the types of questions and formulate a strategy for the type of question.
    Examine how the response effectively addresses the instruction, noting the use of specific details and the structure of the answer.
    
    Example Instruction & Output:
    {example_instruction_output}
    
    {initial_User_Message}
    
    Current Instruction to Respond:
    {current_instruction}
    
    All the tasks to complete: 
    -------------
    Task 1: Answer the Current Instruction

    Description: Provide a direct response to the current instruction from the dataset.
    Instructions: Analyze the instruction carefully and draft a response that fully addresses the query or requirement.
    Output Format: Respond in JSON format as follows: 'instruction': 'question', 'answer': 'your_answer'
    
    Task 2: Evaluate the Response for Accuracy and Completeness

    Description: Assess the initial response for its accuracy and completeness relative to the instruction.
    Instructions: Review the response to ensure that it correctly interprets the instruction and provides all necessary information or answers all parts of the question.
    Output Format: Provide feedback in JSON format: 'evaluation': 'feedback on accuracy and completeness', 'suggested improvements': 'specific suggestions for improvement'.
    
    Task 3: Check for Clarity and Conciseness

    Description: Ensure that the response is clear and concise, free from unnecessary details or ambiguity.
    Instructions: Examine the response to ensure that it is straightforward, avoiding any vague or redundant content.
    Output Format: Feedback should be provided in JSON format: 'clarity_check': 'feedback on clarity and conciseness', 'suggested edits': 'specific edits to enhance clarity'.
    
    Task 4: Validate Factual Information

    Description: Verify all factual information presented in the response to ensure its accuracy and reliability.
    Instructions: Cross-check all facts against reliable sources and note any discrepancies or errors.
    Output Format: Summarize findings in JSON format: 'fact_check': 'list of checked facts', 'errors_found': 'details of any inaccuracies', 'corrections_suggested': 'correct information'.
    Task 5: Refine and Finalize the Response

    Description: Incorporate all feedback and corrections to finalize the response, ensuring it is well-structured and polished.
    Instructions: Revise the response based on the evaluations from previous tasks, making sure to address each point of feedback and correction.
    Output Format: Final response in JSON format: 'instruction': 'question', 'answer': 'your_revised_answer'.
            
    {post_algo_instruct}
    """


    #old_user_message =  f"Answer the question {current_instruction}, give the response in json in the format 'instruction: question, answer: your_answer'  "
    return system_message,user_message


def make_gpt_prompt_alpaca_wit_grade(current_instruction, example_instruction_output):
    """
    Guide the creation of a response for the alpaca_eval dataset by examining the current instruction,
    comparing it to an example instruction and its output, and effectively formulating an answer.

    Args:
        current_instruction (str): The current instruction requiring a response.
        example_instruction_output (str): An example instruction paired with its output to aid in understanding response expectations.

    Returns:
        Tuple[str, str]: A tuple containing a system message and a user message.
    """

    system_message = """
    As an AI trained to assist with the answering questions, your goal is to generate concise and precise answers to the provided instructions.
    This guide will help you step by step to formulate responses that are not only correct but also well-informed and contextually relevant.
    """



    initial_User_Message = "Welcome to your task dashboard for the Alpaca_Eval dataset. Please review the question in the dataset and start with the first uncompleted task. Focus on generating accurate and comprehensive responses. Refer to any previous tasks if needed to maintain continuity and accuracy."

    pre_algo_instruct = "Before we start answering questions from the Alpaca_Eval dataset, ensure you understand the context and requirements of each question. You will be provided with the question and expected to research and draft a response based on reliable sources. Pay close attention to the specifics of each question to tailor your responses appropriately."

    post_algo_instruct = "After drafting your response, review it against the example outputs provided for quality and comprehensiveness. Ensure your final response aligns with the expected format and detail as illustrated by successful examples. Reflect on any feedback or revisions suggested in the dataset guidelines to optimize your response before submission."

    rubric = """
    Alpaca Eval Response Grading Rubric
1. Accuracy (30 Points)
30 Points: The response is factually correct and provides an accurate answer to the given instruction.
20 Points: The response contains minor inaccuracies that do not significantly alter the correctness of the answer.
10 Points: The response contains significant inaccuracies that affect the correctness of the answer.
0 Points: The response is factually incorrect or entirely irrelevant to the given instruction.

2. Relevance (25 Points)
25 Points: The response directly addresses the instruction, with all parts of the response clearly related to the question.
15 Points: The response generally addresses the instruction, but some parts may be tangentially related.
10 Points: The response addresses the instruction only minimally, with much of the content being irrelevant.
0 Points: The response does not address the given instruction.

3. Completeness (20 Points)
20 Points: The response thoroughly answers all components of the instruction, leaving no aspect unaddressed.
15 Points: The response covers most parts of the instruction, but misses one or two minor details.
10 Points: The response partially answers the instruction, missing a significant component or detail.
0 Points: The response provides no meaningful information regarding the instruction.

4. Clarity and Structure (15 Points)
15 Points: The response is clearly articulated and well-structured, making it easy to follow and understand.
10 Points: The response is mostly clear but may have some structural or grammatical issues that slightly hinder understanding.
5 Points: The response has major issues with clarity or structure that make it difficult to understand.
0 Points: The response is incoherent or poorly structured to the extent that it is unintelligible.

5. Creativity or Analytical Depth (10 Points)
10 Points: The response shows exceptional creativity or deep analytical insight relevant to the question.
7 Points: The response is somewhat creative or shows some level of depth in analysis.
4 Points: The response is basic, with no significant creativity or analytical depth.
0 Points: The response is clichéd, trivial, or lacks any creativity or analysis.

Additional Comments and Scoring Guidance
Feedback: Provide specific examples from the response to justify the score awarded in each category.
Scoring Adjustment: Consider any extenuating circumstances that might impact the response's effectiveness, such as complex or unusual instructions.
Final Score: Sum up the scores from each category to give a final score out of 100.
Example Usage of Rubric
For the instruction "What are the names of some famous actors that started their careers on Broadway?", a response listing relevant actors with correct names and context would score highly in accuracy, relevance, and completeness but might score lower in creativity unless additional interesting facts or insights were included.
    """


    user_message = f"""
    ---------------
  
    
    {pre_algo_instruct}
    
    ---------------

    Analyze the Example Instruction and Output:
    Analyse the types of questions and formulate a strategy for the type of question.
    Examine how the response effectively addresses the instruction, noting the use of specific details and the structure of the answer.
    
    Example Instruction & Output:
    {example_instruction_output}
    
    {initial_User_Message}
    
    Current Instruction to Respond:
    {current_instruction}
    
    All the tasks to complete: 
    -------------
    Task 1: Answer the Current Instruction

    Description: Provide a direct response to the current instruction from the dataset.
    Instructions: Analyze the instruction carefully and draft a response that fully addresses the query or requirement.
    Output Format: Respond in JSON format as follows: 'instruction': 'question', 'answer': 'your_answer'
    
    Task 2: Evaluate the Response for Accuracy and Completeness

    Description: Assess the initial response for its accuracy and completeness relative to the instruction.
    Instructions: Review the response to ensure that it correctly interprets the instruction and provides all necessary information or answers all parts of the question.
    Output Format: Provide feedback in JSON format: 'evaluation': 'feedback on accuracy and completeness', 'suggested improvements': 'specific suggestions for improvement'.
    
    Task 3: Check for Clarity and Conciseness

    Description: Ensure that the response is clear and concise, free from unnecessary details or ambiguity.
    Instructions: Examine the response to ensure that it is straightforward, avoiding any vague or redundant content.
    Output Format: Feedback should be provided in JSON format: 'clarity_check': 'feedback on clarity and conciseness', 'suggested edits': 'specific edits to enhance clarity'.
    
    Task 4: Validate Factual Information

    Description: Verify all factual information presented in the response to ensure its accuracy and reliability.
    Instructions: Cross-check all facts against reliable sources and note any discrepancies or errors.
    Output Format: Summarize findings in JSON format: 'fact_check': 'list of checked facts', 'errors_found': 'details of any inaccuracies', 'corrections_suggested': 'correct information'.
    
    Task 5: Refine and Finalize the Response

    Description: Incorporate all feedback and corrections to finalize the response, ensuring it is well-structured and polished.
    Instructions: Revise and rewrite the response based on the evaluations and feedback from previous tasks :'Evaluate the Response for Accuracy and Completeness', 'Check for Clarity and Conciseness', 'Validate Factual Information' , 'making sure to address each point of feedback and correction'.
    Fix the mistakes, and make sure the response is clear, concise, and accurate.
    
    Task 6 : Score the Response
    Description: Use the rubric provided in the instructions to score the final response from 0 to 100. Consider the accuracy, clarity, and completeness of the response when assigning a score.",
    Instructions:  Rubric : {rubric}
    Output Format: Form the Final response based on the answer from Taskref::Refine and Finalize the Response along with the score and feedback in the JSON format.
    Example output format : {{
    "instruction": "What year was the Yamato Battleship built?",
    "answer": "The Yamato Battleship was built in 1940.",
    "Feedback": {{
        "accuracy": "The response is factually correct and provides an accurate answer to the given instruction.",
        "relevance": "The response directly addresses the instruction, with all parts of the response clearly related to the question.",
        "completeness": "The response thoroughly answers the instruction, leaving no aspect unaddressed.",
        "clarity_and_structure": "The response is clearly articulated and well-structured, making it easy to follow and understand.",
        "creativity_or_analytical_depth": "The response is basic, with no significant creativity or analytical depth."
    }},
    "Score": {{
        "accuracy": 30,
        "relevance": 25,
        "completeness": 20,
        "clarity_and_structure": 15,
        "creativity_or_analytical_depth": 4,
        "final_score": 94
    }},
    "Excepted_output": "The Yamato Battleship was built in 1941."
}}
    The final response should definitely contain the score and final score for all type of questions.
    {post_algo_instruct}
    """


    #old_user_message =  f"Answer the question {current_instruction}, give the response in json in the format 'instruction: question, answer: your_answer'  "
    return system_message,user_message

def make_gpt_prompt_alpaca_wit_grade_COV(current_instruction, example_instruction_output):
    """
    Guide the creation of a response for the alpaca_eval dataset by examining the current instruction,
    comparing it to an example instruction and its output, and effectively formulating an answer.

    Args:
        current_instruction (str): The current instruction requiring a response.
        example_instruction_output (str): An example instruction paired with its output to aid in understanding response expectations.

    Returns:
        Tuple[str, str]: A tuple containing a system message and a user message.
    """

    system_message = """
    As an AI trained to assist with the answering questions, your goal is to generate concise and precise answers to the provided instructions.
    This guide will help you step by step to formulate responses that are not only correct but also well-informed and contextually relevant.
    """



    initial_User_Message = "Welcome to your task dashboard for the Alpaca_Eval dataset. Please review the question in the dataset and start with the first uncompleted task. Focus on generating accurate and comprehensive responses. Refer to any previous tasks if needed to maintain continuity and accuracy."

    pre_algo_instruct = "Before we start answering questions from the Alpaca_Eval dataset, ensure you understand the context and requirements of each question. You will be provided with the question and expected to research and draft a response based on reliable sources. Pay close attention to the specifics of each question to tailor your responses appropriately."

    post_algo_instruct = "After drafting your response, review it against the example outputs provided for quality and comprehensiveness. Ensure your final response aligns with the expected format and detail as illustrated by successful examples. Reflect on any feedback or revisions suggested in the dataset guidelines to optimize your response before submission."

    rubric = """
    Alpaca Eval Response Grading Rubric
1. Accuracy (30 Points)
30 Points: The response is factually correct and provides an accurate answer to the given instruction.
20 Points: The response contains minor inaccuracies that do not significantly alter the correctness of the answer.
10 Points: The response contains significant inaccuracies that affect the correctness of the answer.
0 Points: The response is factually incorrect or entirely irrelevant to the given instruction.

2. Relevance (25 Points)
25 Points: The response directly addresses the instruction, with all parts of the response clearly related to the question.
15 Points: The response generally addresses the instruction, but some parts may be tangentially related.
10 Points: The response addresses the instruction only minimally, with much of the content being irrelevant.
0 Points: The response does not address the given instruction.

3. Completeness (20 Points)
20 Points: The response thoroughly answers all components of the instruction, leaving no aspect unaddressed.
15 Points: The response covers most parts of the instruction, but misses one or two minor details.
10 Points: The response partially answers the instruction, missing a significant component or detail.
0 Points: The response provides no meaningful information regarding the instruction.

4. Clarity and Structure (15 Points)
15 Points: The response is clearly articulated and well-structured, making it easy to follow and understand.
10 Points: The response is mostly clear but may have some structural or grammatical issues that slightly hinder understanding.
5 Points: The response has major issues with clarity or structure that make it difficult to understand.
0 Points: The response is incoherent or poorly structured to the extent that it is unintelligible.

5. Creativity or Analytical Depth (10 Points)
10 Points: The response shows exceptional creativity or deep analytical insight relevant to the question.
7 Points: The response is somewhat creative or shows some level of depth in analysis.
4 Points: The response is basic, with no significant creativity or analytical depth.
0 Points: The response is clichéd, trivial, or lacks any creativity or analysis.

Additional Comments and Scoring Guidance
Feedback: Provide specific examples from the response to justify the score awarded in each category.
Scoring Adjustment: Consider any extenuating circumstances that might impact the response's effectiveness, such as complex or unusual instructions.
Final Score: Sum up the scores from each category to give a final score out of 100.
Example Usage of Rubric
For the instruction "What are the names of some famous actors that started their careers on Broadway?", a response listing relevant actors with correct names and context would score highly in accuracy, relevance, and completeness but might score lower in creativity unless additional interesting facts or insights were included.
    """


    user_message = f"""
    ---------------
  
    
    {pre_algo_instruct}
    
    ---------------

    Analyze the Example Instruction and Output:
    Analyse the types of questions and formulate a strategy for the type of question.
    Examine how the response effectively addresses the instruction, noting the use of specific details and the structure of the answer.
    
    Example Instruction & Output:
    {example_instruction_output}
    
    {initial_User_Message}
    
    Current Instruction to Respond:
    {current_instruction}
    
    All the tasks to complete: 
    -------------
    
Task 1:  Generate Baseline Response by answering the Current Instruction

Description: Produce an initial draft response to the given instruction.
Instructions: Using the LLM, generate a response that attempts to answer the question based on the model's knowledge.
Output Format: JSON format: {{"instruction": "question", "baseline_response": "your_initial_answer"}}


Task 2: Plan Verifications

Description: Develop a set of verification questions that test the factual accuracy and relevance of the baseline response.
Instructions: Identify potential factual claims in the baseline response and formulate specific questions to verify each claim.
Output Format: JSON format: {{"verification_questions": ["Question 1", "Question 2", ...]}}

Task 3 : Execute Verifications

Description: Address each verification question independently to validate the baseline response.
Instructions: Use the LLM or external databases to find answers to each verification question without bias from the baseline response.
Output Format: JSON format: {{"verification_answers": {{"Question 1": "Answer", "Question 2": "Answer", ...}}}}

Task 4 : Generate Final Verified Response

Description: Integrate the insights from the verification process to revise and finalize the response.
Instructions: Reassess and rewrite the baseline response considering the answers from the verification stage{{Taskref :: Execute Verifications}} and correct any inaccuracies or enhance the response based on this new information.
Output Format: JSON format: {{"instruction": "question", "final_response": "revised_answer"}}

Task 5 : Score the Response
    Description: Use the rubric provided in the instructions to score the final response from 0 to 100. Consider the accuracy, clarity, and completeness of the response when assigning a score.",
    Instructions:  Rubric : {rubric}
    Output Format: Form the Final response based on the answer from Taskref::Refine and Finalize the Response along with the score and feedback in the JSON format.
    Example output format : {{
    "instruction": "Which year india won the first world cup in cricket?",
    ""baseline_response": "India won the first world cricket cup in 1985"
    "final_response": "India won the first world cricket cup in 1981.",
    "Excepted_output": "India won the first world cricket cup in 1981."
    "Feedback": {{
        "accuracy": "The response is factually correct and provides an accurate answer to the given instruction.",
        "relevance": "The response directly addresses the instruction, with all parts of the response clearly related to the question.",
        "completeness": "The response thoroughly answers the instruction, leaving no aspect unaddressed.",
        "clarity_and_structure": "The response is clearly articulated and well-structured, making it easy to follow and understand.",
        "creativity_or_analytical_depth": "The response is basic, with no significant creativity or analytical depth."
    }},
    "Score": {{
        "accuracy": 30,
        "relevance": 25,
        "completeness": 20,
        "clarity_and_structure": 15,
        "creativity_or_analytical_depth": 4,
        "final_score": 94
    }},
    {{"verification_questions": ["Question 1", "Question 2", ...]}},
    {{"verification_answers": {{"Question 1": "Answer", "Question 2": "Answer", ...}}}},
   
}}
    The final response should definitely contain the score and final score for all type of questions.
    
    {post_algo_instruct}
    """


    #old_user_message =  f"Answer the question {current_instruction}, give the response in json in the format 'instruction: question, answer: your_answer'  "
    return system_message,user_message




###########useful prompts 
# Task 6 : Documentation and Reflection

# Description: Document the process and reflect on the outcomes.
# Instructions: Provide a detailed account of the verification process and the rationale behind the final response modifications. Reflect on the effectiveness of the CoVe method in reducing inaccuracies and enhancing the response quality.
# Output Format: JSON format: {"documentation": "detailed_process_description", "reflection": "effectiveness_of_verification_process"}