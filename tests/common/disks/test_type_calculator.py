"""Tests for astdiskd message definitions."""

from pathlib import Path

import pytest

from astoria.common.disks import DiskType, DiskTypeCalculator

DATA_PATH = Path("tests/data/disk_types")


@pytest.mark.parametrize(
    "folder,disk_type",
    [
        ("metadata", DiskType.METADATA),
        ("noaction", DiskType.NOACTION),
        ("update", DiskType.UPDATE),
        ("usercode", DiskType.USERCODE),
        ("usercode_alt_entrypoint", DiskType.USERCODE),
        ("usercode_zip", DiskType.NOACTION),
    ],
)
def test_disk_type_determination(folder: str, disk_type: DiskType) -> None:
    """Test that we can correctly determine the type of disk."""
    calculator = DiskTypeCalculator("robot.py")
    assert calculator.calculate(DATA_PATH / folder) is disk_type
