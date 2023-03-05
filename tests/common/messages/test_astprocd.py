"""Tests for astprocd message definitions."""
from pathlib import Path

from astoria import __version__
from astoria.common.code_status import CodeStatus
from astoria.common.disks import DiskInfo, DiskType, DiskUUID
from astoria.common.ipc import ProcessManagerMessage


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
        pid=8335,
    )

    assert (
        pmm.json()
        == f'{{"status": "RUNNING", "astoria_version": "{__version__}", "code_status": "code_running", "disk_info": {{"uuid": "foobar", "mount_path": "/mnt", "disk_type": "NOACTION"}}, "pid": 8335}}'  # noqa: E501
    )
