# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys, os
sys.path.insert(0, os.path.abspath('../../src'))
sys.path.insert(1, os.path.abspath('../..'))
sys.path.insert(2, os.path.abspath(os.path.join(os.path.dirname(__file__), '_ext')))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Factory creator'
copyright = '2026, Jakub Oliver Kubin'
author = 'Jakub Oliver Kubin'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc', 
    'sphinx.ext.napoleon', 
    'myst_parser',
    'sphinxcontrib.mermaid',
    'sphinx_needs',
    'sphinx_design',
    'sphinx.ext.mathjax',
    'github_release_assets'
]

myst_fence_as_directive = ['mermaid']
myst_enable_extensions = [
    'colon_fence',
    'dollarmath'
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
#html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
