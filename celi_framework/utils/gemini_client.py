"""
Google Gemini client for CELI framework.

This module provides integration with Google's Gemini models through the
generative AI library, following CELI's patterns for LLM clients.
"""

import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from celi_framework.utils.llm_response import LLMResponse
from celi_framework.utils.log import app_logger


def configure_gemini():
    """Configure Gemini API with credentials from environment."""
    # Try both GEMINI_API_KEY and GOOGLE_API_KEY for compatibility
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    app_logger.debug(f"Configured Gemini with API key: {api_key[:10]}...")


async def gemini_chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gemini-1.5-flash",
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> LLMResponse:
    """
    Send a chat completion request to Gemini.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Gemini model name (e.g., 'gemini-1.5-flash', 'gemini-2.5-flash')
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens to generate
        **kwargs: Additional parameters (ignored for compatibility)
        
    Returns:
        LLMResponse object with the generated content
    """
    # Always configure to ensure API key is set
    configure_gemini()
    
    # Extract model name - remove 'gemini-' prefix if passed with it
    if model.startswith("gemini-"):
        model_name = model
    else:
        model_name = f"gemini-{model}"
    
    app_logger.info(f"Calling Gemini model: {model_name}")
    
    # Convert messages to Gemini format
    # Gemini expects a simple prompt string for non-chat models
    # For now, we'll concatenate messages into a single prompt
    prompt_parts = []
    
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
    
    prompt = "\n\n".join(prompt_parts)
    
    # Create model instance
    gemini_model = genai.GenerativeModel(model_name)
    
    # Build generation config
    generation_config = {}
    if temperature is not None:
        generation_config["temperature"] = temperature
    if max_tokens is not None:
        generation_config["max_output_tokens"] = max_tokens
    
    try:
        # Generate response
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(**generation_config) if generation_config else None
        )
        
        # Convert to LLMResponse format
        # Handle safety filters or empty responses
        if response.candidates and response.candidates[0].content.parts:
            content = response.text
        else:
            # Response was blocked or empty
            content = ""
            if response.candidates and response.candidates[0].finish_reason:
                finish_reason = response.candidates[0].finish_reason
                if finish_reason == 2:  # SAFETY
                    content = "[Response blocked by safety filters]"
                elif finish_reason == 3:  # MAX_TOKENS
                    content = "[Response truncated due to max tokens]"
                else:
                    content = f"[Response ended with finish_reason: {finish_reason}]"
        
        return LLMResponse(
            content=content,
            messages=messages,
            model=model_name,
            finish_reason="stop",
            tool_calls=None,
            prompt_tokens=0,  # Gemini doesn't provide token counts in response
            completion_tokens=0,
            total_tokens=0,
            cost=0.0  # Would need to calculate based on pricing
        )
        
    except Exception as e:
        app_logger.error(f"Gemini API error: {str(e)}")
        raise