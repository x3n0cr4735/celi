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
    'sphinx.ext.viewcode',
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
import subprocess

logging.basicConfig(level=logging.INFO)

sys.path.insert(0, os.path.abspath(".."))

# def add_subfolders_to_path(folder):
#     for dirpath, _, _ in os.walk(folder):
#         sys.path.insert(0, dirpath)

# # Add examples and experiments subfolders
# add_subfolders_to_path(os.path.abspath('../celi_framework/examples'))
# add_subfolders_to_path(os.path.abspath('../celi_framework/experiments'))



sys.path.insert(0, os.path.abspath('../celi_framework'))
sys.path.insert(0, os.path.abspath('../celi_framework/examples'))
sys.path.insert(0, os.path.abspath('../celi_framework/experiments'))
def run_apidoc(app):
    """Run sphinx-apidoc to generate .rst files."""
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(cur_dir, '..', '..'))
    examples_dir = os.path.join(project_root, 'celi_framework', 'examples')
    experiments_dir = os.path.join(project_root, 'celi_framework', 'experiments')
    output_dir = os.path.join(cur_dir, '_gen')

    if os.path.exists(examples_dir):
        subprocess.check_call(['sphinx-apidoc', '-o', output_dir, examples_dir])
    else:
        print(f"Warning: {examples_dir} does not exist.")

    if os.path.exists(experiments_dir):
        subprocess.check_call(['sphinx-apidoc', '-o', output_dir, experiments_dir])
    else:
        print(f"Warning: {experiments_dir} does not exist.")

def setup(app):
    app.connect('builder-inited', run_apidoc)
print(f"sys.path: {sys.path}")