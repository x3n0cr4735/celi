"""
Hybrid LLM tools for CELI framework.

This module provides tools that enable job descriptions to leverage multiple LLMs
for different tasks, implementing a hybrid approach where each model is used for
its strengths.
"""

from typing import Optional, Dict, Any
from celi_framework.utils.llms import quick_ask
from celi_framework.utils.log import app_logger


class HybridLLMTools:
    """Tools for using multiple LLMs in a single job description."""
    
    def __init__(self, default_model: Optional[str] = None, **kwargs):
        """
        Initialize hybrid LLM tools.
        
        Args:
            default_model: Default model to use if not specified in tool calls
            **kwargs: Additional configuration
        """
        self.default_model = default_model or "claude-sonnet-4-20250514"
        self.config = kwargs
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the schema for available hybrid LLM tools."""
        return {
            "tools": [
                {
                    "name": "ask_llm",
                    "description": "Send a prompt to a specific LLM model",
                    "parameters": {
                        "prompt": "The prompt to send to the model",
                        "model": "The model to use (e.g., 'gemini-2.5-flash', 'claude-sonnet-4-20250514')",
                        "temperature": "Optional temperature (0.0-2.0)",
                        "max_tokens": "Optional max tokens to generate"
                    }
                },
                {
                    "name": "ask_for_code", 
                    "description": "Ask an LLM optimized for code generation",
                    "parameters": {
                        "prompt": "The coding task or question",
                        "language": "Optional programming language",
                        "model": "Optional model override (defaults to code-optimized model)"
                    }
                },
                {
                    "name": "ask_for_analysis",
                    "description": "Ask an LLM optimized for analysis and reasoning",
                    "parameters": {
                        "prompt": "The analysis task or question",
                        "model": "Optional model override (defaults to analysis-optimized model)"
                    }
                },
                {
                    "name": "fix_code_with_llm",
                    "description": "Fix code issues using a code-optimized LLM",
                    "parameters": {
                        "code": "The code to fix",
                        "error_description": "Description of the error or issue",
                        "test_failures": "Optional test failure details",
                        "model": "Optional model override (defaults to code-fixing model)"
                    }
                }
            ]
        }
    
    def ask_llm(self, prompt: str, model: Optional[str] = None, 
                temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        """
        Send a prompt to a specific LLM model.
        
        Args:
            prompt: The prompt to send
            model: The model to use (defaults to configured default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            The model's response
        """
        model = model or self.default_model
        
        app_logger.info(f"Hybrid LLM: Sending prompt to {model}")
        
        try:
            response = quick_ask(
                prompt=prompt,
                model_name=model,
                temperature=temperature,
                max_tokens=max_tokens,
                verbose=True
            )
            return response
        except Exception as e:
            app_logger.error(f"Error calling {model}: {str(e)}")
            return f"Error calling {model}: {str(e)}"
    
    def ask_for_code(self, prompt: str, language: Optional[str] = None, 
                     model: Optional[str] = None) -> str:
        """
        Ask an LLM optimized for code generation.
        
        Args:
            prompt: The coding task or question  
            language: Optional programming language
            model: Optional model override
            
        Returns:
            Generated code
        """
        # Default to Gemini for code generation based on our testing
        model = model or "gemini-2.5-flash"
        
        code_prompt = f"You are an expert programmer. Generate clean, well-commented code.\n\n"
        if language:
            code_prompt += f"Language: {language}\n\n"
        code_prompt += f"Task: {prompt}\n\n"
        code_prompt += "Return only the code, no explanations."
        
        return self.ask_llm(code_prompt, model=model, temperature=0.2)
    
    def ask_for_analysis(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Ask an LLM optimized for analysis and reasoning.
        
        Args:
            prompt: The analysis task or question
            model: Optional model override
            
        Returns:
            Analysis response
        """
        # Default to Claude for analysis based on our testing
        model = model or "claude-sonnet-4-20250514"
        
        analysis_prompt = f"You are an expert analyst. Provide thorough, insightful analysis.\n\n"
        analysis_prompt += f"Task: {prompt}\n\n"
        analysis_prompt += "Be comprehensive but concise."
        
        return self.ask_llm(analysis_prompt, model=model, temperature=0.3)
    
    def fix_code_with_llm(self, code: str, error_description: str, 
                         test_failures: Optional[str] = None, 
                         model: Optional[str] = None) -> str:
        """
        Fix code issues using a code-optimized LLM.
        
        Args:
            code: The code to fix
            error_description: Description of the error
            test_failures: Optional test failure details
            model: Optional model override
            
        Returns:
            Fixed code
        """
        # Default to Gemini for code fixing based on our testing
        model = model or "gemini-2.5-flash"
        
        fix_prompt = f"""You are an expert debugger. Fix the following code.

CURRENT CODE:
```python
{code}
```

ERROR DESCRIPTION:
{error_description}
"""
        
        if test_failures:
            fix_prompt += f"""
TEST FAILURES:
{test_failures}
"""
        
        fix_prompt += """
REQUIREMENTS:
1. Fix ONLY the specific issues described
2. Maintain all existing functionality
3. Use additive enhancement - don't remove existing code
4. Add clear comments explaining your fixes
5. Return the complete, corrected code

Return only the fixed Python code, no explanations."""
        
        return self.ask_llm(fix_prompt, model=model, temperature=0.2, max_tokens=20000)