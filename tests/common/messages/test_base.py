"""Tests for abstract message definitions."""

import pytest
from pydantic import ValidationError

from astoria import __version__
from astoria.common.messages.base import ManagerStatusMessage


def test_manager_status_enum() -> None:
    """Test that the status enum is as expected."""
    StatEnum = ManagerStatusMessage.ManagerStatus

    assert len(StatEnum) == 3
    assert StatEnum.STOPPED.value == "STOPPED"
    assert StatEnum.STARTING.value == "STARTING"
    assert StatEnum.RUNNING.value == "RUNNING"


def test_manager_status_fields() -> None:
    """Test that the fields on the status message work."""
    message = ManagerStatusMessage(
        status=ManagerStatusMessage.ManagerStatus.STOPPED,
    )

    assert message.status == ManagerStatusMessage.ManagerStatus.STOPPED
    assert message.astoria_version == __version__

    assert message.json() == '{"status": "STOPPED", "astoria_version": "0.1.0"}'


def test_manager_status_subclass():
    """Test that we can create a subclass."""
    class MyManagerStatusMessage(ManagerStatusMessage):

        custom_field: int

    message = MyManagerStatusMessage(
        status=MyManagerStatusMessage.ManagerStatus.RUNNING,
        custom_field=12,
    )

    assert message.status == ManagerStatusMessage.ManagerStatus.RUNNING
    assert message.astoria_version == __version__
    assert message.custom_field == 12

    assert message.json() == \
        '{"status": "RUNNING", "astoria_version": "0.1.0", "custom_field": 12}'

    # Check for Validation Error
    with pytest.raises(ValidationError):
        MyManagerStatusMessage(status=MyManagerStatusMessage.ManagerStatus.RUNNING)
