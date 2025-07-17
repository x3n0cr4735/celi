# CELI Framework Examples

This directory contains examples demonstrating various features and capabilities of the CELI framework.

## ⚠️ IMPORTANT: API KEY REQUIREMENTS ⚠️

**ALWAYS EXPORT API KEYS IN YOUR COMMAND LINE!**

When running ANY example in this directory, you MUST export the required API keys as environment variables in your command:

```bash
# For Claude/Anthropic examples:
export ANTHROPIC_API_KEY=your-key-here && python example_script.py

# For OpenAI/GPT examples:
export OPENAI_API_KEY=your-key-here && python example_script.py

# For Google Gemini examples:
export GOOGLE_API_KEY=your-key-here && python example_script.py

# For hybrid examples using multiple models:
export ANTHROPIC_API_KEY=your-key && export GOOGLE_API_KEY=your-key && python hybrid_example.py
```

**DO NOT rely on .env files alone!** The API libraries often check environment variables before our code can load .env files.

## Available Examples

### Parser Challenge (`parser_challenge/`)
Advanced example showing how to adapt document parsers for different bank formats using a hybrid LLM approach. This includes:
- Hybrid LLM tools for leveraging multiple models
- Integration tests for the hybrid system
- Example job descriptions using different LLM strategies

## Running Examples

1. Activate your virtual environment:
```bash
source .venv/bin/activate  # or your preferred venv activation
```

2. Export required API keys (see above)

3. Run the example:
```bash
python example_script.py
```

## Troubleshooting

If you get errors like:
- "No API_KEY or ADC found"
- "ANTHROPIC_API_KEY not found"
- "OPENAI_API_KEY not set"

**YOU FORGOT TO EXPORT THE API KEY!** See the instructions above.

## Creating New Examples

When creating new examples:
1. Always include clear API key requirements in comments
2. Consider using multiple models for complex tasks
3. Follow the patterns established in existing examples
4. Add your example to this README