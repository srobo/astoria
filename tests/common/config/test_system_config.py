"""Test the config."""

import sys
from pathlib import Path
from typing import Type

import pytest
from pydantic import ValidationError

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


from astoria.common.config import AstoriaConfig


class TestSystemConfig:
    """Test that we can load the system config."""

    @pytest.mark.parametrize(
        "filename",
        ["missing_optional.toml", "valid.toml"],
    )
    def test_config_loads_valid_files(self, filename: Path, data_dir: Path) -> None:
        """Test that we can load valid config files."""
        with open(data_dir / "config" / filename, "rb") as fh:
            AstoriaConfig.load_from_file(fh)

    @pytest.mark.parametrize(
        "filename,exception",
        [
            ("bad_types.toml", ValidationError),
            ("extraneous_fields.toml", ValidationError),
            ("missing_required.toml", ValidationError),
            ("not.toml", tomllib.TOMLDecodeError),
        ],
    )
    def test_config_raises_correct_exception(
        self,
        filename: Path,
        exception: Type[Exception],
        data_dir: Path,
    ) -> None:
        """Test for bad type validation."""
        with pytest.raises(exception):
            with open(data_dir / "config" / filename, "rb") as fh:
                AstoriaConfig.load_from_file(fh)
