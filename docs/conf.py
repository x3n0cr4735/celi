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



sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../celi_framework'))
def run_apidoc(app):
    """Run sphinx-apidoc to generate .rst files."""
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(cur_dir, '..'))
    celi_framework_dir = os.path.join(project_root, 'celi_framework')
    output_dir = os.path.join(cur_dir, '_gen')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    combined_output_file = os.path.join(output_dir, 'api_reference.rst')
    with open(combined_output_file, 'w') as f:
        f.write("API Reference\n")
        f.write("=============\n\n")

        for sub_dir_name in os.listdir(celi_framework_dir):
            sub_dir = os.path.join(celi_framework_dir, sub_dir_name)
            if os.path.isdir(sub_dir):
                subprocess.check_call(['sphinx-apidoc', '-o', output_dir, sub_dir])
                f.write(f"{sub_dir_name.capitalize()}\n")
                f.write("=" * len(sub_dir_name.capitalize()) + "\n\n")
                for root, dirs, files in os.walk(os.path.join(output_dir, f'celi_framework.{sub_dir_name}')):
                    for file in files:
                        if file.endswith('.rst'):
                            module = os.path.splitext(file)[0]
                            f.write(f"`{module} <../_gen/{module}>`_\n\n")
                            f.write(".. toctree::\n   :hidden:\n\n")
                            f.write(f"   ../_gen/{module}\n\n")
                f.write("\n")
            else:
                print(f"Warning: {sub_dir} does not exist or is not a directory.")

def setup(app):
    app.connect('builder-inited', run_apidoc)

print(f"sys.path: {sys.path}")
