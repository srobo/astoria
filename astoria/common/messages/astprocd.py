"""Message schemas for astprocd."""
from enum import Enum
from typing import Optional

from astoria.common.ipc import ManagerMessage

from .astdiskd import DiskInfo


class CodeStatus(str, Enum):
    """Status of the running code."""

    STARTING = "code_starting"
    RUNNING = "code_running"
    KILLED = "code_killed"
    FINISHED = "code_finished"
    CRASHED = "code_crashed"


class ProcessManagerMessage(ManagerMessage):
    """
    Status message for Process Manager.

    Published to astoria/astprocd
    """

    code_status: Optional[CodeStatus]
    disk_info: Optional[DiskInfo]
