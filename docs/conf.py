import astoria

project = "Astoria"
copyright = "2020-23, Dan Trickey"  # noqa: A001
author = "Dan Trickey"

release = astoria.__version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.graphviz",
    "sphinx_rtd_theme",
    "sphinx-pydantic",
    "sphinx_click",
    "myst_parser",
]

templates_path: list[str] = []

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

html_theme = "sphinx_rtd_theme"

html_static_path: list[str] = []

autodoc_default_options = {
    "member-order": "alphabetical",
    "special-members": "__init__",
    "undoc-members": True,
    # "inherited-members": True,
}

autodoc_mock_imports = []

nitpick_ignore = [
    ("py:data", "DiskUUID"),
    ("py:func", "typing.NewType"),
]

source_suffix = [".rst", ".md"]
