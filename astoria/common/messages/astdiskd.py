"""MQTT message definitions for astdiskd."""
from typing import Dict

from astoria.common.disks import DiskInfo, DiskUUID
from astoria.common.ipc import ManagerMessage


class DiskManagerMessage(ManagerMessage):
    """
    Status message for Disk Manager.

    Published to /astoria/astdiskd
    """

    disks: Dict[DiskUUID, DiskInfo]
