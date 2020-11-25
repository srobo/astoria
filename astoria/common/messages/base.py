"""Common data for MQTT messages."""
from enum import Enum

from pydantic import BaseModel

from astoria import __version__


class BaseManagerStatusMessage(BaseModel):
    """Common data that all manager status messages output."""

    class ManagerStatus(Enum):
        """Running Status of the manager daemon."""

        STOPPED = "STOPPED"
        STARTING = "STARTING"
        RUNNING = "RUNNING"

    status: ManagerStatus
    astoria_version: str = __version__
