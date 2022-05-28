"""Test the config."""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


from astoria.common.config import AstoriaConfig

DATA_PATH = Path("tests/data/config")

GOOD_FILES = {"missing_optional.toml", "valid.toml"}


def load_config(fn: str) -> None:
    """Load a config file."""
    path = DATA_PATH / fn
    with open(path, "rb") as fh:
        AstoriaConfig.load_from_file(fh)


def test_config_loads_valid_files() -> None:
    """Test that we can load valid config files."""
    for good_file in GOOD_FILES:
        load_config(good_file)


def test_exception_on_bad_type() -> None:
    """Test for bad type validation."""
    with pytest.raises(ValidationError):
        load_config("bad_types.toml")


def test_exception_on_extraneous_field() -> None:
    """Test for extraneous field validation."""
    with pytest.raises(ValidationError):
        load_config("extraneous_fields.toml")


def test_exception_on_missing_required() -> None:
    """Test for missing required field validation."""
    with pytest.raises(ValidationError):
        load_config("missing_required.toml")


def test_exception_on_invalid_toml() -> None:
    """Test for roml validation."""
    with pytest.raises(tomllib.TOMLDecodeError):
        load_config("not.toml")
