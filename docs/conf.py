from typing import List

import astoria

project = "Astoria"
copyright = "2020-21, Dan Trickey"  # noqa: A001
author = "Dan Trickey"

release = astoria.__version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    'sphinx.ext.autosectionlabel',
    "sphinx_rtd_theme",
    "sphinx-pydantic",
    "m2r2",
]

templates_path = []  # type: List[str]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

html_theme = "sphinx_rtd_theme"

html_static_path = []  # type: List[str]

autodoc_default_options = {
    "member-order": "alphabetical",
    "special-members": "__init__",
    "undoc-members": True,
    # "inherited-members": True,
}

autodoc_mock_imports = []

source_suffix = [".rst", ".md"]