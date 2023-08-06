# -*- coding: utf-8 -*-

import os
import sys
from ast import parse

from sphinx.ext.napoleon.docstring import GoogleDocstring

confpath = os.path.dirname(__file__)
sys.path.append(confpath)
rootpath = os.path.join(confpath, "..", "..")
sys.path.append(rootpath)


with open(os.path.join("../../trinidi", "__init__.py")) as f:
    package_version = (
        parse(next(filter(lambda line: line.startswith("__version__"), f))).body[0].value.s
    )


## See
##   https://github.com/sphinx-doc/sphinx/issues/2115
##   https://michaelgoerz.net/notes/extending-sphinx-napoleon-docstring-sections.html
##
# first, we define new methods for any new sections and add them to the class
def parse_keys_section(self, section):
    return self._format_fields("Keys", self._consume_fields())


GoogleDocstring._parse_keys_section = parse_keys_section


def parse_attributes_section(self, section):
    return self._format_fields("Attributes", self._consume_fields())


GoogleDocstring._parse_attributes_section = parse_attributes_section


def parse_class_attributes_section(self, section):
    return self._format_fields("Class Attributes", self._consume_fields())


GoogleDocstring._parse_class_attributes_section = parse_class_attributes_section


# we now patch the parse method to guarantee that the the above methods are
# assigned to the _section dict
def patched_parse(self):
    self._sections["keys"] = self._parse_keys_section
    self._sections["class attributes"] = self._parse_class_attributes_section
    self._unpatched_parse()


GoogleDocstring._unpatched_parse = GoogleDocstring._parse
GoogleDocstring._parse = patched_parse


confpath = os.path.dirname(__file__)
sys.path.append(confpath)

on_rtd = os.environ.get("READTHEDOCS") == "True"


# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
rootpath = os.path.abspath("../..")
sys.path.insert(0, rootpath)

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "4.2.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinxcontrib.bibtex",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.mathjax",
    "sphinx.ext.todo",
    "nbsphinx",
    "IPython.sphinxext.ipython_console_highlighting",
]

bibtex_bibfiles = ["references.bib"]

nbsphinx_execute = "never"
nbsphinx_prolog = """
.. raw:: html

    <style>
    .nbinput .prompt, .nboutput .prompt {
        display: none;
    }
    div.highlight {
        background-color: #f9f9f4;
    }
    p {
        margin-bottom: 0.8em;
        margin-top: 0.8em;
    }
    </style>
"""


# See
#  https://stackoverflow.com/questions/2701998#62613202
#  https://github.com/JamesALeedham/Sphinx-Autosummary-Recursion
autosummary_generate = True

# Copied from scikit-learn sphinx configuration
if os.environ.get("NO_MATHJAX"):
    extensions.append("sphinx.ext.imgmath")
    imgmath_image_format = "svg"
else:
    extensions.append("sphinx.ext.mathjax")
    mathjax_path = "https://cdn.mathjax.org/mathjax/latest/" "MathJax.js?config=TeX-AMS_HTML"

mathjax_config = {
    "TeX": {
        "Macros": {
            "mb": [r"\mathbf{#1}", 1],
            "mbs": [r"\boldsymbol{#1}", 1],
            "mbb": [r"\mathbb{#1}", 1],
            "norm": [r"\lVert #1 \rVert", 1],
            "abs": [r"\left| #1 \right|", 1],
            "argmin": [r"\mathop{\mathrm{argmin}}"],
            "sign": [r"\mathop{\mathrm{sign}}"],
            "prox": [r"\mathrm{prox}"],
            "loss": [r"\mathop{\mathrm{loss}}"],
            "kp": [r"k_{\|}"],
            "rp": [r"r_{\|}"],
        }
    }
}


# See https://stackoverflow.com/questions/5599254
autoclass_content = "both"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The encoding of source files.
source_encoding = "utf-8"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "TRINIDI"
copyright = "2023 Thilo Balke"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = package_version
# The full version, including alpha/beta/rc tags.
release = version

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    "tmp",
    "*.tmp.*",
    "*.tmp",
]

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "default"


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages. See the documentation for
# a list of builtin themes.
html_theme = "furo"

html_theme_options = {
    "sidebar_hide_name": True,
}


# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None
html_logo = "_static/trinidi_logo.svg"

# The name of an image file (within the static path) to use as favicon of the
# docs. This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "_static/trinidi_favicon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
if on_rtd:
    html_static_path = []
else:
    html_static_path = ["_static"]

# Output file base name for HTML help builder.
htmlhelp_basename = "TRINIDIdoc"

# Include TOODs
todo_include_todos = True


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ("index", "trinidi.tex", "TRINIDI Documentation", "Thilo Balke", "manual"),
]


latex_engine = "xelatex"

# latex_use_xindy = False

latex_macros = []
for k, v in mathjax_config["TeX"]["Macros"].items():
    if len(v) == 1:
        latex_macros.append(r"\newcommand{\%s}{%s}" % (k, v[0]))
    else:
        latex_macros.append(r"\newcommand{\%s}[1]{%s}" % (k, v[0]))

latex_elements = {"preamble": "\n".join(latex_macros)}


# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
}
# Added timeout due to periodic scipy.org down time
# intersphinx_timeout = 30

# napoleon_include_init_with_doc = True
napoleon_use_ivar = True
napoleon_use_rtype = False

# See https://github.com/sphinx-doc/sphinx/issues/9119
# napoleon_custom_sections = [("Returns", "params_style")]


graphviz_output_format = "svg"
inheritance_graph_attrs = dict(rankdir="LR", fontsize=9, ratio="compress", bgcolor="transparent")
inheritance_node_attrs = dict(
    shape="box",
    fontsize=9,
    height=0.4,
    margin='"0.08, 0.03"',
    style='"rounded,filled"',
    fillcolor='"#f4f4ffff"',
)


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [("index", "trinidi", "Thilo Balke", ["Thilo Balke"], 1)]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ("index",),
]


if on_rtd:
    print("Building on ReadTheDocs\n")
    print("Current working directory: {}".format(os.path.abspath(os.curdir)))
    import numpy as np

    print("NumPy version: %s" % np.__version__)
    import matplotlib

    matplotlib.use("agg")


print("rootpath: %s" % rootpath)
print("confpath: %s" % confpath)

# Sort members by type
autodoc_default_options = {
    "member-order": "bysource",
    "inherited-members": False,
    "ignore-module-all": False,
    "show-inheritance": True,
    "members": True,
    "special-members": "__call__",
}
autodoc_docstring_signature = True
autoclass_content = "both"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "**tests**", "**spi**", "**README.rst", "include"]


def setup(app):
    # app.add_css_file("trinidi.css")
    app.add_css_file(
        "http://netdna.bootstrapcdn.com/font-awesome/4.7.0/" "css/font-awesome.min.css"
    )
