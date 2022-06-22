# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/stable/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('..'))
from skactiveml import pool, __version__

from docs.generate import generate_strategy_overview_rst, \
    generate_api_reference_rst, generate_examples, generate_tutorials

# -- Project information -----------------------------------------------------

project = 'scikit-activeml'
copyright = '2020'
author = 'Daniel Kottke, Marek Herde, Pham Minh Tuan, Pascal Mergard, Christoph Sandrock'

# The short X.Y version
version = __version__
# The full version, including alpha/beta/rc tags
release = __version__

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx_gallery.gen_gallery',
    'sphinxcontrib.bibtex',
    'nbsphinx',
    'numpydoc'
]

# nbsphinx_execute = 'always'

# Napoleon settings
napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_references = True
numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ['.rst']

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Set the paths for the sphinx_gallery extension:
sphinx_gallery_conf = {
    'run_stale_examples': False,
    'line_numbers': True,

    # path to your example scripts
    'examples_dirs': os.path.normpath('generated/examples'),

    # the path where to save gallery generated output
    'gallery_dirs': os.path.normpath('generated/sphinx_gallery_examples'),

    'matplotlib_animations': True,

    # directory where function/class granular galleries are stored
    'backreferences_dir':
        os.path.normpath('generated/sphinx_gallery_backreferences'),

    # Modules for which function/class level galleries are created.
    'doc_module': ('skactiveml',),

    'reference_url': {
        # The module you locally document uses None
        'skactiveml': None
    }
}
os.makedirs(os.path.abspath(sphinx_gallery_conf['gallery_dirs']),
            exist_ok=True)

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

html_logo = 'logos/scikit-activeml-logo.png'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "github_url": "https://github.com/scikit-activeml/scikit-activeml",
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/scikit-activeml",
            "icon": "fas fa-box",
        }
    ],
    "icon_links_label": "Quick Links"
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'scikit-activeml-guide'

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'scikit-activeml', 'scikit-activeml -- User Guide',
     [author], 1)
]

# -- Extension configuration -------------------------------------------------

# -- Options for bibtex extension --------------------------------------------

bibtex_bibfiles = ['refs.bib']
# bibtex_encoding = 'latin'

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    'numpy': ('https://numpy.org/doc/stable/', None),
    'python': ('https://docs.python.org/3/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
    "matplotlib": ("https://matplotlib.org/", None),
    "joblib": ("https://joblib.readthedocs.io/en/latest/", None),
    "iteration-utilities": (
    "https://iteration-utilities.readthedocs.io/en/latest/", None)
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Generate files for strategy overview and api reference ------------------

autosummary_generate = True

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'inherited-members': True,
#    'special-members': False
}

autoclass_content = 'class'

generate_api_reference_rst(
    gen_path=os.path.abspath('generated')
)

examples_data = generate_examples(
    gen_path=os.path.abspath('generated'),
    package=pool,
    json_path=os.path.abspath('examples/pool'))

generate_strategy_overview_rst(
    gen_path=os.path.abspath('generated'),
    examples_data=examples_data
)

generate_tutorials(
    src_path=os.path.abspath('../tutorials/'),
    dst_path=os.path.abspath('generated/tutorials/'),
)