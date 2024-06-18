# LLM Support

CELI uses the OpenAI APIs by default to make LLM calls.  Out of the box these APIs hit OpenAI, but they can work with any LLM compatible with 
that API.  Many frameworks currently support this API, including Ollama, vLLM, and nVidia NIMs.  We show an example here using vLLM.  Others
will work similarly.

## vLLM

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

## Pointing CELI to your vLLM server

Use the --model-api-url option with CELI to point to your vLLM server.  You should also set your OPENAI_API_TOKEN to the
value you set for `api-key` when you started vLLM.

