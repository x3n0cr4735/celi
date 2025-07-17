"""
Example job description showcasing advanced hybrid LLM strategies.

This example demonstrates how to use different LLMs for their strengths:
- Claude for analysis, planning, and orchestration
- Gemini for code generation and fixing
- GPT-4 for creative solutions or fallback

The job itself is run by the PRIMARY_LLM (Claude), but specific tasks
delegate to other models through the hybrid tools.
"""

from celi_framework.core.job_description import JobDescription, Task
from celi_framework.examples.parser_challenge.hybrid_llm_tools import HybridLLMTools


# Example: Code Review and Improvement Workflow
code_review_job = JobDescription(
    role="""You are a senior software architect conducting code reviews. 
    You leverage multiple AI models to provide comprehensive feedback:
    - Use Claude (yourself) for architectural analysis and design patterns
    - Use Gemini for specific code improvements and optimizations
    - Use GPT-4 for generating alternative implementations""",
    
    context="""You're reviewing a Python module that needs improvement in terms of:
    1. Code quality and readability
    2. Performance optimization
    3. Error handling
    4. Test coverage""",
    
    task_list=[
        Task(
            task_name="analyze_architecture",
            details={
                "description": "Analyze the overall architecture and design",
                "instructions": """
1. Review the code structure and identify design patterns
2. Note any architectural issues or anti-patterns
3. Suggest high-level improvements
Note: This uses your native Claude capabilities for analysis"""
            }
        ),
        
        Task(
            task_name="generate_optimized_code",
            details={
                "description": "Generate optimized version using Gemini",
                "instructions": """
1. Use ask_for_code with model='gemini-2.5-flash' to generate an optimized version
2. Focus on performance improvements and clean code practices
3. Ensure the optimized code maintains all functionality"""
            }
        ),
        
        Task(
            task_name="create_comprehensive_tests",
            details={
                "description": "Generate comprehensive test suite",
                "instructions": """
1. Use ask_for_code with model='gemini-2.5-flash' to generate unit tests
2. Include edge cases and error scenarios
3. Aim for high code coverage"""
            }
        ),
        
        Task(
            task_name="generate_alternative_approach",
            details={
                "description": "Get creative alternative implementation",
                "instructions": """
1. Use ask_llm with model='gpt-4' to brainstorm alternative approaches
2. Ask for innovative solutions or different paradigms
3. Compare with the original approach"""
            }
        ),
        
        Task(
            task_name="fix_specific_issues",
            details={
                "description": "Fix any identified bugs or issues",
                "instructions": """
1. If any bugs were found, use fix_code_with_llm to fix them
2. Provide the error description and let Gemini handle the fix
3. Verify the fix resolves the issue"""
            }
        ),
        
        Task(
            task_name="synthesize_recommendations",
            details={
                "description": "Synthesize all findings and provide recommendations",
                "instructions": """
1. Combine insights from all models
2. Provide a prioritized list of improvements
3. Include code snippets from the various model outputs
Note: This uses your native Claude capabilities for synthesis"""
            }
        )
    ],
    
    tool_implementations_class=HybridLLMTools,
    
    pre_context_instruct="""Remember: You (Claude) are orchestrating this review, 
    but you can delegate specific tasks to other models through the hybrid tools. 
    Each model has its strengths - use them wisely.""",
    
    post_context_instruct="""Ensure all recommendations are practical and actionable. 
    The goal is to leverage the best capabilities of each model to provide 
    comprehensive, high-quality code review feedback.""",
    
    monitor_instructions="""Track which model provided which insights. 
    This helps understand the value each model brings to the workflow.""",
    
    initial_user_message="""Please review this Python module and provide 
    comprehensive feedback using the hybrid approach."""
)


# Example 2: Multi-Model Research Assistant
research_job = JobDescription(
    role="""You are a research assistant that leverages multiple AI models 
    to provide comprehensive research on technical topics.""",
    
    context="""You need to research a technical topic thoroughly by:
    1. Understanding the fundamentals (Claude)
    2. Finding code examples (Gemini)  
    3. Exploring creative applications (GPT-4)""",
    
    task_list=[
        Task(
            task_name="understand_fundamentals",
            details={
                "description": "Research and explain the core concepts",
                "instructions": """
1. Use your analytical capabilities to break down the topic
2. Identify key concepts, principles, and relationships
3. Create a structured overview"""
            }
        ),
        
        Task(
            task_name="gather_code_examples",
            details={
                "description": "Find practical code implementations",
                "instructions": """
1. Use ask_for_code with model='gemini-2.5-flash' to generate example code
2. Request examples for different use cases
3. Include both simple and advanced examples"""
            }
        ),
        
        Task(
            task_name="explore_creative_uses",
            details={
                "description": "Brainstorm innovative applications",
                "instructions": """
1. Use ask_llm with model='gpt-4' to explore creative applications
2. Ask for unconventional use cases or combinations with other technologies
3. Think outside the box"""
            }
        ),
        
        Task(
            task_name="create_tutorial",
            details={
                "description": "Synthesize findings into a tutorial",
                "instructions": """
1. Combine insights from all sources
2. Create a structured tutorial with theory and practice
3. Include the best examples from each model"""
            }
        )
    ],
    
    tool_implementations_class=HybridLLMTools,
    
    initial_user_message="Research the topic of async programming in Python"
)


# Example 3: Hybrid Debugging Assistant
debugging_job = JobDescription(
    role="""You are a debugging expert that uses multiple AI models to 
    diagnose and fix complex issues.""",
    
    context="""A complex bug needs to be diagnosed and fixed. You'll use:
    - Claude for root cause analysis
    - Gemini for generating fixes
    - Multiple models for verification""",
    
    task_list=[
        Task(
            task_name="analyze_symptoms",
            details={
                "description": "Analyze the bug symptoms and context",
                "instructions": """
1. Review error messages, logs, and code context
2. Identify patterns and potential causes
3. Form hypotheses about the root cause"""
            }
        ),
        
        Task(
            task_name="reproduce_issue",
            details={
                "description": "Create minimal reproduction",
                "instructions": """
1. Use ask_for_code with model='gemini-2.5-flash' to create reproduction code
2. Isolate the issue to its simplest form
3. Verify the reproduction shows the same bug"""
            }
        ),
        
        Task(
            task_name="generate_fixes",
            details={
                "description": "Generate multiple fix approaches",
                "instructions": """
1. Use fix_code_with_llm with your error analysis
2. Also use ask_llm with model='gpt-4' for alternative fixes
3. Compare different approaches"""
            }
        ),
        
        Task(
            task_name="verify_fixes",
            details={
                "description": "Verify and test the fixes",
                "instructions": """
1. Test each proposed fix
2. Use ask_for_analysis to evaluate which fix is best
3. Consider edge cases and side effects"""
            }
        )
    ],
    
    tool_implementations_class=HybridLLMTools,
    
    monitor_instructions="""Ensure fixes are thoroughly tested and don't 
    introduce new issues. Document which model provided the best solution.""",
    
    initial_user_message="Debug this async race condition issue..."
)