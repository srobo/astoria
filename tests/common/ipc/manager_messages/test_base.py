"""Tests for abstract message definitions."""

import pytest
from pydantic import ValidationError

from astoria import __version__
from astoria.common.ipc import ManagerMessage


def test_manager_status_enum() -> None:
    """Test that the status enum is as expected."""
    StatEnum = ManagerMessage.Status

    assert len(StatEnum) == 2
    assert StatEnum.STOPPED.value == "STOPPED"
    assert StatEnum.RUNNING.value == "RUNNING"


def test_manager_status_fields() -> None:
    """Test that the fields on the status message work."""
    message = ManagerMessage(
        status=ManagerMessage.Status.STOPPED,
    )

    assert message.status == ManagerMessage.Status.STOPPED
    assert message.astoria_version == __version__

    assert message.json() == \
        f'{{"status": "STOPPED", "astoria_version": "{__version__}"}}'


def test_manager_status_subclass() -> None:
    """Test that we can create a subclass."""
    class MyManagerStatusMessage(ManagerMessage):

        custom_field: int

    message = MyManagerStatusMessage(
        status=MyManagerStatusMessage.Status.RUNNING,
        custom_field=12,
    )

    assert message.status == ManagerMessage.Status.RUNNING
    assert message.astoria_version == __version__
    assert message.custom_field == 12

    assert message.json() == \
        f'{{"status": "RUNNING", "astoria_version": "{__version__}", "custom_field": 12}}'

    # Check for Validation Error
    with pytest.raises(ValidationError):
        MyManagerStatusMessage(status=MyManagerStatusMessage.Status.RUNNING)
