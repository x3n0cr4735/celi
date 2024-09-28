# Change Log

## 0.3.7 (September 28, 2024)
* Added initial support for OpenAI o1 models
* Big improvements to loop detection
* Handle errors/bad JSON in the builtin review
* Allow built-in review to skip updating the system prompt (useful for long system prompts)
* Improved Anthropic support - handle rate limiting correctly
* Support additional AWS Bedrock models besides Anthropic
* Bug fix with command line option --force-tool-every-n 

## 0.3.6 (August 12, 2024)
* Many changes to improve performance with Claude
* Added a new command line option --force-tool-every-n
* Fixes #91 - Anthropic model temp=None issues
* Fixes #90 - quick_ask stack overflow
* Made the builtin review more robust
* Fixes #87 - missing new initial user message
* Better logging of token budget errors
* Changed pop_context to complete_section
* Update Wikipedia example

## 0.3.5 (July 14, 2024)

* Added `--sequential` option to turn off parallelization.
* Added support for Claude models using Anthropic APIs and Amazon Bedrock
* Improved loop detection
* Added exponential backoff if rate limits are hit
* Revised the README
* Fixes #79 - per call max-token not working

## 0.3.4 (June 23, 2024)

* Added --token-budget option to limit the number of LLM calls made.
* Fixes #71 - only error logs are red
* Fixes #74 - only check most recent messages for duplicates.

## 0.3.3 (June 18, 2024)

* Changed write_string_to_file to default to UTF-8 and allow other encodings.

## 0.3.2 (June 15, 2024)

* Updated seed database for LLM cache

## 0.3.1 (June 15, 2024)

* Updated seed database for LLM cache

## 0.3.0 (June 15, 2024)

* Removed many dependencies from the core framework and moved them into extras
* Made HumanEval the default use case and provide a prefilled cache with LLM responses.
* Created a simplified demo and added --simulate-live
* Removed requirement for MongoDB

## 0.2.2 (May 12, 2024)

* Added server.py containing a REST API for CELI as well as WebSockets for continuous updates
* Added a celi-react-demo which is a prototype React front end for the Wikipedia use case that demonstrates the server.
* Added the ability to provide asynchronous human feedback on any section at any time.
* Added new examples - GRE, AP_English_Language, and AP_English_Literature

## 0.2.1 (May 12, 2024)

* Updated the HumanEval use case with additional results 

## 0.2.0 (May 6, 2024)
* Changed to 0.2.0 because there is an API change (tools should now inherit from `BaseDocToolImplementations` instead of `ToolImplementations`)
* Moved writing of the document into the tools.  This allows CELI to be used for tasks that don't involve document 
generation, and also allows draft documents to be updated by multiple tasks.
* `BaseDocToolImplementations` has a `save_draft_section` section that writes the draft document.
* Added HumanEval example that gets 88.89% correct.
* Improved the error handling when the LLM generates a bad function call.  This is now fed back for correction rather 
than throwing an uncaught exception.
* Several minor code cleanup and logging improvements.

### Upgrading to 0.2.0
* ToolImplementations that write documents (previously all of them) must be changed to derive from 
`BaseDocToolImplementations` instead of `ToolImplementations`.  Also, some prompts may need to be updated 
to indicate that the tools are now responsible for writing the final output.  That used to be handled directly
by the CELI processor.

## 0.1.0 (Apr 21, 2024)   
* First "release" release

## 0.0.19 (Apr 20, 2024)
* Fixing .env load for OS X

## 0.0.18 (Apr 20, 2024)
* Fixing .env load

## 0.0.17 (Apr 20, 2024)
* Fixing tool config

## 0.0.16 (Apr 19, 2024)
* Fixing tool config

## 0.0.15 (Apr 18, 2024)
* Minor doc tweaks

## 0.0.14 (Apr 18, 2024)
* Minor doc tweaks

## 0.0.13 (Apr 18, 2024)
* Fixing example use case

## 0.0.12 (Apr 18, 2024)
* Fixing example use case

## 0.0.11 (Apr 18, 2024)
* Reorganized doc

## 0.0.10 (Apr 18, 2024)
* Made repo public

## 0.0.9 (Apr 7, 2024)

* Initial release with documentation

