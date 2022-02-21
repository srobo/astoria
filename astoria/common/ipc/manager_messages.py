"""Manager Messages."""
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel

from astoria import __version__
from astoria.common.code_status import CodeStatus
from astoria.common.disks import DiskInfo, DiskUUID
from astoria.common.metadata import Metadata


class ManagerMessage(BaseModel):
    """Common data that all manager messages output."""

    class Status(Enum):
        """Running Status of the manager daemon."""

        STOPPED = "STOPPED"
        RUNNING = "RUNNING"

    status: Status
    astoria_version: str = __version__


class ProcessManagerMessage(ManagerMessage):
    """
    Status message for Process Manager.

    Published to astoria/astprocd
    """

    code_status: Optional[CodeStatus]
    disk_info: Optional[DiskInfo]


class MetadataManagerMessage(ManagerMessage):
    """
    Status message for Metadata Manager.

    Published to /astoria/astmetad
    """

    metadata: Metadata


class DiskManagerMessage(ManagerMessage):
    """
    Status message for Disk Manager.

    Published to /astoria/astdiskd
    """

    disks: Dict[DiskUUID, DiskInfo]
