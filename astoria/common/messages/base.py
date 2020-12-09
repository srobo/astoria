"""Common data for MQTT messages."""
from enum import Enum

from pydantic import BaseModel

from astoria import __version__


class ManagerMessage(BaseModel):
    """Common data that all manager messages output."""

    class Status(Enum):
        """Running Status of the manager daemon."""

        STOPPED = "STOPPED"
        RUNNING = "RUNNING"

    status: Status
    astoria_version: str = __version__
