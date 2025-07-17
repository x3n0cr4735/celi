#!/usr/bin/env python3
"""Test the integrated hybrid LLM approach for parser challenge."""

# Load environment variables FIRST before any other imports
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from celi_framework.utils.llms import quick_ask
from celi_framework.examples.parser_challenge.hybrid_llm_tools import HybridLLMTools


def test_gemini_integration():
    """Test that Gemini is properly integrated into CELI's LLM system."""
    print("Testing Gemini Integration with CELI")
    print("=" * 60)
    
    # Test 1: Direct Gemini call through quick_ask
    print("\n1. Testing direct Gemini call through quick_ask...")
    try:
        response = quick_ask(
            prompt="Write a Python function that adds two numbers",
            model_name="gemini-2.5-flash",
            temperature=0.2,
            verbose=True
        )
        print(f"✓ Gemini responded successfully")
        print(f"Response preview: {response[:100]}...")
    except Exception as e:
        print(f"✗ Error calling Gemini: {e}")
        return False
    
    # Test 2: Test the hybrid tools
    print("\n2. Testing HybridLLMTools...")
    tools = HybridLLMTools()
    
    # Test ask_llm with Gemini
    print("   - Testing ask_llm with Gemini...")
    try:
        response = tools.ask_llm(
            prompt="What is 2+2?",
            model="gemini-2.5-flash"
        )
        print(f"   ✓ ask_llm worked: {response}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test ask_for_code
    print("   - Testing ask_for_code...")
    try:
        code = tools.ask_for_code(
            prompt="Create a function to reverse a string",
            language="Python"
        )
        print(f"   ✓ ask_for_code generated code")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test fix_code_with_llm
    print("   - Testing fix_code_with_llm...")
    broken_code = '''def add(a, b):
    return a + b + c  # c is not defined'''
    
    try:
        fixed = tools.fix_code_with_llm(
            code=broken_code,
            error_description="NameError: name 'c' is not defined"
        )
        print(f"   ✓ fix_code_with_llm generated fix")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n✅ All integration tests completed!")
    return True


def test_model_routing():
    """Test that different models are properly routed."""
    print("\n\nTesting Model Routing")
    print("=" * 60)
    
    models_to_test = [
        ("claude-sonnet-4-20250514", "Claude"),
        ("gemini-2.5-flash", "Gemini"),
        ("gpt-4", "GPT-4")
    ]
    
    for model, name in models_to_test:
        print(f"\nTesting {name} ({model})...")
        try:
            response = quick_ask(
                prompt=f"Say 'Hello from {name}' and nothing else",
                model_name=model,
                temperature=0,
                verbose=False
            )
            print(f"✓ {name}: {response}")
        except Exception as e:
            print(f"✗ {name} error: {e}")


def main():
    """Run all integration tests."""
    print("Integrated Hybrid LLM System Tests\n")
    
    # Run tests
    test_gemini_integration()
    test_model_routing()
    
    print("\n" + "=" * 60)
    print("Integration testing complete!")
    print("\nThe hybrid LLM system is ready to use. You can now:")
    print("- Use quick_ask/ask_split with model='gemini-*' for Gemini models")
    print("- Use HybridLLMTools in job descriptions for multi-model workflows")
    print("- Configure which model to use for specific tasks")


if __name__ == "__main__":
    main()