# Change Log

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

