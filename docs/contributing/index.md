# Contributing

Thank you for your interest in CELI! ✨

CELI welcomes contributions of all forms. This section of CELI's documentation serves as a resource to help you to contribute to the project.

## Poetry

Dependencies are managed using [Poetry].  After cloning the repo, run poetry from the root directory:

`poetry install`

This will create a virtual environment in the `.venv` directory and install all dependencies there.

`poetry shell` will open a shell in that virtual environment.

## Building docs

Change to the docs directory and run `make html`

Any warnings in the doc build will cause the real doc build to fail.

For more work on docs, run `sphinx-autobuild docs docs/_build/html --port 8001`.  This starts a live updating server for the docs.

Docstrings can be generated using the useful [gpt4docstrings](https://github.com/MichaelisTrofficus/gpt4docstrings) library.

`gpt4docstrings -w -st numpy -m gpt-4 --ignore-nested-functions substreams.py`
