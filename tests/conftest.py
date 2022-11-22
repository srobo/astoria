"""PyTest Fixtures."""
from pathlib import Path

import pytest

from astoria.common.config import AstoriaConfig


@pytest.fixture
def data_dir() -> Path:
    """The tests data directory."""
    return Path("tests/data")


@pytest.fixture
def config(data_dir: Path) -> AstoriaConfig:
    """A valid system config."""
    config_path = data_dir / "config/valid.toml"
    with config_path.open("rb") as fh:
        return AstoriaConfig.load_from_file(fh)
