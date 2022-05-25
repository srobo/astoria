"""Tests for astdiskd message definitions."""

from pathlib import Path

from astoria.common.disks import DiskType, DiskTypeCalculator

DATA_PATH = Path("tests/data/disk_types")


def test_disk_type_determination() -> None:
    """Test that we can correctly determine the type of disk."""
    expected_results = {
        "metadata": DiskType.METADATA,
        "noaction": DiskType.NOACTION,
        "update": DiskType.UPDATE,
        "usercode": DiskType.USERCODE,
        "usercode_alt_entrypoint": DiskType.USERCODE,
        "usercode_zip": DiskType.NOACTION,
    }

    calculator = DiskTypeCalculator("robot.py")

    for path, disk_type in expected_results.items():
        assert calculator.calculate(DATA_PATH / path) is disk_type
