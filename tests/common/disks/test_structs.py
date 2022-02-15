"""Tests for astdiskd message definitions."""

from pathlib import Path

from astoria.common.disks import DiskInfo, DiskType, DiskUUID

DATA_PATH = Path("tests/data/disk_types")


def test_disk_type_enum() -> None:
    """Test that DiskType has the right values."""
    assert DiskType.NOACTION.value == "NOACTION"
    assert DiskType.UPDATE.value == "UPDATE"
    assert DiskType.USERCODE.value == "USERCODE"
    assert DiskType.METADATA.value == "METADATA"


def test_disk_type_determination() -> None:
    """Test that we can correctly determine the type of disk."""
    expected_results = {
        "metadata": DiskType.METADATA,
        "noaction": DiskType.NOACTION,
        "update": DiskType.UPDATE,
        "usercode": DiskType.USERCODE,
    }

    for path, disk_type in expected_results.items():
        assert DiskType.determine_disk_type(DATA_PATH / path) is disk_type


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

    assert info.json() == \
        '{"uuid": "foobar", "mount_path": "/mnt", "disk_type": "NOACTION"}'
