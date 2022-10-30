"""Test that the astoria imports as expected."""

import astoria_old


def test_module() -> None:
    """Test that the module behaves as expected."""
    assert astoria_old.__version__ is not None
