# LLM Support

CELI uses OpenAI GPT-4 by default for LLM calls, but it does support other LLMs.  You can change the LLM to use
with the `--primary-model-name` option. You can use other OpenAI models, use Anthropic Claude models, or use vLLM
or any other server that serves an OpenAI compatible API.  

## Other OpenAI models

Any of the OpenAI models can be selected with the `--primary-model-name` option.  See the 
[OpenAI Models page](https://platform.openai.com/docs/models) for all the currently available options.

## Claude models

The Claude models from Anthropic are also support, but through the Anthropic APIs and Amazon Bedrock.

### Using the Anthropic API

To use the Anthropic APIs, get an Anthropic API key and use the ANTHROPIC_API_KEY environment variable or 
the `--anthropic-api-key` command line option.  Claude models names are available on the 
[Claude model page](https://docs.anthropic.com/en/docs/about-claude/models#model-names).  

```bash
  python -m celi_framework.main \
  --job-description=celi_framework.examples.human_eval.job_description.job_description \
  --anthropic-api-key=<Insert your OpenAI API key here> \
  --model-name=claude-3-5-sonnet-20240620
```  

### Using Amazon Bedrock

To use Amazon Bedrock with the Claude models, there are a couple preliminary steps you need to do.
1. Set up default AWS keys.  You can set up an `.aws/credentials` file or set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables.
2. Enable the Claude models in AWS.  You can use the [Bedrock AWS Console](https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/models) for this.  Note, models are enabled per region.  To use the Anthropic APIs, get an Anthropic API key and use the ANTHROPIC_API_KEY environment variable or
3. If the AWS region is not assigned using the environment variable AWS_REGION or passed directly to LLM calls as aws_region, the default is us-west-2. For more info on model available by region, see [Model support by AWS Region](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html).
4. Text completions are currently enabled for all Bedrock models, but tools are only integrated for Anthropic models.

When used through Bedrock, the Claude model name start with `anthropic.`.  Model availability
varies by region.  For more info see the [Claude model docs](https://docs.anthropic.com/en/docs/about-claude/models#model-names).

Example - note that the AWS login credentials need to be set for this to work:
```bash
  python -m celi_framework.main \
  --job-description=celi_framework.examples.human_eval.job_description.job_description \
  --model-name=anthropic.claude-3-sonnet-20240229-v1:0
```  
See the [Anthropic Amazon Bedrock documentation](https://docs.anthropic.com/en/api/claude-on-amazon-bedrock)

## vLLM

Many frameworks currently support the OpenAI API, including Ollama, vLLM, and nVidia NIMs.  We show an example here 
using vLLM.  Others will work similarly.

[vLLM](https://docs.vllm.ai/en/stable/getting_started/installation.html) is an LLM serving framework.  To use CELI with
vLLM, you first set up a vLLM server hosting the LLM that you want to use, and then point CELI to use that model.

### Setting up vLLM

There are many options for setting up vLLM.  In this example we just cover very basic usage.  Please refer to the vLLM 
docs for more info.

* Install vLLM using `pip install vllm`.
* Start the vLLM server.  The following comment runs a small microsoft phi-3 model.

    python -m vllm.entrypoints.openai.api_server \
      --model microsoft/Phi-3-mini-4k-instruct \
      --dtype auto \
      --trust-remote-code \
      --api-key local-token \
      --chat-template ./template_phi3.jinja

### Customizing the chat template

Among other setup options, you may need to customize the chat template.  FOr example, the default phi3 template does
not support the system messages used by CELI, and it expects alternating "user" and "assistant" messages, which doesn't
always occur with CELI.  Here is an updated chat template that handles those cases:

```{include} ./template_phi3.jinja
```

For a fully functional version, you would have to extend it also for tool usage.

### Pointing CELI to your vLLM server

Use the --model-api-url option with CELI to point to your vLLM server.  You should also set your OPENAI_API_TOKEN to the
value you set for `api-key` when you started vLLM.

