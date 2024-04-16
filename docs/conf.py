# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "celi-framework"
copyright = "2024, Jan-Samuel Wagner"
author = "Jan-Samuel Wagner"
release = "0.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

source_suffix = [".rst", ".md"]

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx.ext.intersphinx",
    "sphinxext.opengraph",
    "sphinx_copybutton",
    "sphinx.ext.extlinks",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",  # for google style docstrings
]

myst_enable_extensions = [
    "attrs_inline",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_logo = "logo.png"
html_title = "CELI"
html_theme_options = {
    "navigation_with_keys": True,
}

# -- Links -------------------------------------------------
extlinks = {
    #'fastapi-sec': ('https://fastapi.tiangolo.com/%s', 'FastAPI '),
}

# -- Puts code on the path for API generation -------------------------------------------------
import os
import sys

import logging

logging.basicConfig(level=logging.INFO)

sys.path.insert(0, os.path.abspath(".."))
print(f"sys.path: {sys.path}")
