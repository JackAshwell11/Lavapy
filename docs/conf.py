# Configuration file for the Sphinx documentation builder.
#
# See the documentation for me:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import re
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "Lavapy"
copyright = "2021, Aspect1103"
author = "Aspect1103"
with open(os.path.join(os.path.abspath(".."), "lavapy", "__init__.py")) as init:
    release = re.search(r'__version__ = "([\'0-9\'].[\'0-9\'].[\'0-9\'])"', init.read()).group(1)

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx"
]

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
autodoc_member_order = "groupwise"

rst_prolog = """
.. |coro| replace:: This function is a |corourl|_.
.. |maybecoro| replace:: This function *could be a* |corourl|_.
.. |corourl| replace:: *coroutine*
.. _corourl: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""

# Link to other sphinx documentation
intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "aio": ("https://docs.aiohttp.org/en/stable/", None),
    "dpy": ("https://discordpy.readthedocs.io/en/stable/", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes. Also add any paths that contain custom static files
# (such as style sheets) here, relative to this directory. They are copied after
# the builtin static files, so a file named "default.css" will overwrite the
# builtin "default.css".
html_theme = "furo"
html_logo = "logo.png"
