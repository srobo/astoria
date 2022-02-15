"""Tests for astprocd message definitions."""
from pathlib import Path

from astoria import __version__
from astoria.common.disks import DiskInfo, DiskType, DiskUUID
from astoria.common.messages.astprocd import CodeStatus, ProcessManagerMessage


def test_code_status_enum() -> None:
    """Test that CodeStatus has the right values."""
    assert CodeStatus.STARTING.value == "code_starting"
    assert CodeStatus.RUNNING.value == "code_running"
    assert CodeStatus.KILLED.value == "code_killed"
    assert CodeStatus.FINISHED.value == "code_finished"
    assert CodeStatus.CRASHED.value == "code_crashed"
    assert len(CodeStatus) == 5


def test_proc_manager_fields() -> None:
    """Test that the fields on the status message work."""
    info = DiskInfo(
        uuid=DiskUUID("foobar"),
        mount_path=Path("/mnt"),
        disk_type=DiskType.NOACTION,
    )

    pmm = ProcessManagerMessage(
        disk_info=info,
        code_status=CodeStatus.RUNNING,
        status=ProcessManagerMessage.Status.RUNNING,
    )

    assert pmm.json() == f'{{"status": "RUNNING", "astoria_version": "{__version__}", "code_status": "code_running", "disk_info": {{"uuid": "foobar", "mount_path": "/mnt", "disk_type": "NOACTION"}}}}'  # noqa: E501
