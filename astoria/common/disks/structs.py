"""Struct definitions for astdiskd."""
from enum import Enum
from pathlib import Path
from typing import NewType

from pydantic import BaseModel

DiskUUID = NewType('DiskUUID', str)


class DiskType(Enum):
    """Type of disk."""

    USERCODE = "USERCODE"
    METADATA = "METADATA"
    NOACTION = "NOACTION"


class DiskInfo(BaseModel):
    """Information about a mounted disk."""

    uuid: DiskUUID
    mount_path: Path
    disk_type: DiskType
