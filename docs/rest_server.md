# CELI REST Server

You can also run CELI in a server mode to connect it to a front end.  This allows for user interaction and input
into CELI processing both as the processor is running and after it completes.

## REST API

In server mode, CELI provides a simple rest API for interaction with the processor.  The current version of the server
is designed to serve a single use case/job description, but can support multiple simultaneous instances of that job. 

* /sessions/create - Creates a new session and returns the session id.  It initializes the tools based on the data passed into this call.  In the wikipedia example, the data passed into the session are the source and target wikipedia pages.  This instructs the tools on which data to use for processing.
* /session/{session_id}/schema - Returns the schema for the session.  The schema defines the different overall sections that CELI will work on independently.
* /session/{session_id}/updates - The call opens up a websocket session that streams back updates on CELI procsesing, including the working context and final output.
* /session/{session_id}/human_input - Allows human input to be sent into CELI to alter the processing.  This can be done during processing or after final output completes (in which case it will continue the processing in response to the output)

## Running the server

To use CELI in server mode, run celi_framework.server.  To use this mode, you specify an "--init_class" or 
a TOOL_INIT_CLASS environment variable that is the name of a Pydantic model that will be used to initialize the 
ToolImplementations.

For the wikipedia example, this is:
```python
class WikipediaInit(BaseModel):
    example_url: str
    target_url: str
    ignore_updates: bool = False
```

and the corresponding setup in the .env file is:
```
JOB_DESCRIPTION=celi_framework.examples.wikipedia.job_description.job_description
TOOL_INIT_CLASS=celi_framework.examples.wikipedia.tools.WikipediaInit
```

## Demo React App

There is a demo of a React app in examples/celi-react-demo that provides a front end for the Wikipedia use case.
See [Getting started with React app](https://celi.readthedocs.io/en/stable/reference/react_demo_app.html) for more info on how to do that.
