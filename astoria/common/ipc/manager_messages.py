"""Manager Messages."""
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel

from astoria import __version__
from astoria.common.code_status import CodeStatus
from astoria.common.disks import DiskInfo, DiskTypeCalculator, DiskUUID
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

    disks: Dict[DiskUUID, Path]

    def calculate_disk_info(self) -> Dict[DiskUUID, DiskInfo]:
        """
        Calculate the disk info of the disks in the message.

        As astdiskd only gives us information about the path of each disk,
        we need to calculate the type of each disk in the message.

        :returns: A dictionary of disk UUIDs and disk information.
        """
        disk_type_calculator = DiskTypeCalculator()
        return {
            uuid: DiskInfo(
                uuid=uuid,
                mount_path=path,
                disk_type=disk_type_calculator.calculate(path),
            )
            for uuid, path in self.disks.items()
        }
