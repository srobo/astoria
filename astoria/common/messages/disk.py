"""MQTT message definitions for the disk manager daemon."""
from pathlib import Path
from typing import List, NewType

from pydantic import BaseModel

from .base import BaseManagerStatusMessage

DiskUUID = NewType('DiskUUID', str)


class DiskManagerStatusMessage(BaseManagerStatusMessage):
    """
    Status message for Disk Manager.

    Published to /astoria/disk/status.
    """

    disks: List[DiskUUID]


class DiskInfoMessage(BaseModel):
    """
    Information about a mounted disk.

    Published to /astoria/disk/disks/<DiskUUID>
    """

    uuid: DiskUUID
    mount_path: Path
