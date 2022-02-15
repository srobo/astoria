"""Message schemas for astprocd."""
from typing import Optional

from astoria.common.code_status import CodeStatus
from astoria.common.ipc import ManagerMessage

from .astdiskd import DiskInfo


class ProcessManagerMessage(ManagerMessage):
    """
    Status message for Process Manager.

    Published to astoria/astprocd
    """

    code_status: Optional[CodeStatus]
    disk_info: Optional[DiskInfo]
