"""Test the types for astmetad."""
from pathlib import Path

import pytest

from astoria.common.config import AstoriaConfig
from astoria.common.messages.astmetad import Metadata, RobotMode


def load_config() -> AstoriaConfig:
    """Load the config for the tests."""
    path = Path("tests/data/config/valid.toml")
    with open(path, "r") as fh:
        return AstoriaConfig.load_from_file(fh)


def test_metadata_mutation_can_mutate():
    """Test that we can mutate an attr."""
    m = Metadata.init(load_config())
    assert m.arena == "A"
    m.mutate("arena", "B")
    assert m.arena == "B"


def test_metadata_mutation_list_mutable():
    """Test that we can mutate all expected."""
    m = Metadata.init(load_config())
    mutable = {
        ("arena", "C", str),
        ("zone", "2", int),
        ("mode", "COMP", RobotMode),
    }
    for k, v, t in mutable:
        m.mutate(k, v)
        assert isinstance(m.__dict__[k], t)


def test_metadata_mutation_cannot_mutate_immutable():
    """Test that we cannot mutate an immutable attr."""
    m = Metadata.init(load_config())
    assert m.game_timeout is None
    with pytest.raises(ValueError):
        m.mutate("game_timeout", 100000)
    assert m.game_timeout is None


def test_metadata_mutation_cannot_mutate_unknown():
    """Test that we cannot mutate an unknown attr."""
    m = Metadata.init(load_config())
    with pytest.raises(ValueError):
        m.mutate("foo", 100000)


def test_metadata_mutation_cast_types():
    """Test that types are cast to the expected type on mutation."""
    m = Metadata.init(load_config())
    assert m.zone == 0
    assert isinstance(m.zone, int)
    m.mutate("zone", "3")
    assert m.zone == 3
    assert isinstance(m.zone, int)
