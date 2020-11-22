"""MQTT message definitions for the disk manager daemon."""
from enum import Enum
from pathlib import Path
from typing import Dict, List, NewType

from pydantic import BaseModel

from astoria.common.disk_constraints import (
    Constraint,
    FilePresentConstraint,
    TrueConstraint,
)

from .base import BaseManagerStatusMessage

DiskUUID = NewType('DiskUUID', str)


class DiskManagerStatusMessage(BaseManagerStatusMessage):
    """
    Status message for Disk Manager.

    Published to /astoria/disk/status.
    """

    disks: List[DiskUUID]


class DiskType(Enum):
    """Type of disk."""

    USERCODE = "USERCODE"
    METADATA = "METADATA"
    UPDATE = "UPDATE"
    NOACTION = "NOACTION"

    @classmethod
    def determine_disk_type(cls, mount_path: Path) -> 'DiskType':
        """Determine the disk type from the mount path."""
        constraints: Dict['DiskType', Constraint] = {
            cls.USERCODE: FilePresentConstraint("robot.zip"),
            cls.METADATA: FilePresentConstraint("astoria.json"),
            cls.UPDATE: FilePresentConstraint("updatefile.txt"),
            cls.NOACTION: TrueConstraint(),  # Always match
        }

        for typ, constraint in constraints.items():
            if constraint.matches(mount_path):
                return typ

        raise RuntimeError("Unable to determine type of disk.")  # pragma: nocover


class DiskInfoMessage(BaseModel):
    """
    Information about a mounted disk.

    Published to /astoria/disk/disks/<DiskUUID>
    """

    uuid: DiskUUID
    mount_path: Path
    disk_type: DiskType
