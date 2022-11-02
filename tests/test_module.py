"""Test that the astoria imports as expected."""

import astoria


def test_module() -> None:
    """Test that the module behaves as expected."""
    assert astoria.__version__ is not None
