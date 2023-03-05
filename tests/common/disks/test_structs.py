"""Tests for astdiskd message definitions."""

from pathlib import Path

from astoria.common.disks import DiskInfo, DiskType, DiskUUID


def test_disk_type_enum() -> None:
    """Test that DiskType has the right values."""
    assert DiskType.NOACTION.value == "NOACTION"
    assert DiskType.USERCODE.value == "USERCODE"
    assert DiskType.METADATA.value == "METADATA"


def test_disk_info_fields() -> None:
    """Test that the fields on the status message work."""
    info = DiskInfo(
        uuid=DiskUUID("foobar"),
        mount_path=Path("/mnt"),
        disk_type=DiskType.NOACTION,
    )

    assert info.uuid == "foobar"
    assert info.mount_path == Path("/mnt")
    assert info.disk_type == DiskType.NOACTION

    assert (
        info.json() == '{"uuid": "foobar", "mount_path": "/mnt", "disk_type": "NOACTION"}'
    )
