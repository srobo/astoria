"""Test the code status enum."""

from astoria.common.code_status import CodeStatus


def test_code_status_enum() -> None:
    """Test that CodeStatus has the right values."""
    assert CodeStatus.STARTING.value == "code_starting"
    assert CodeStatus.RUNNING.value == "code_running"
    assert CodeStatus.KILLED.value == "code_killed"
    assert CodeStatus.FINISHED.value == "code_finished"
    assert CodeStatus.CRASHED.value == "code_crashed"
    assert len(CodeStatus) == 5
