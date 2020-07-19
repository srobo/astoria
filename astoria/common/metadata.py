"""Metadata Types."""
import platform
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from astoria import __version__


class RobotMode(Enum):
    """Mode of the robot."""

    COMP = "comp"
    DEV = "dev"


class SystemMetadata(BaseModel):
    """The current metadata."""

    @classmethod
    def init(cls) -> 'SystemMetadata':
        """Initialise data."""
        return cls(
            astoria_version=__version__,
            python_version=platform.python_version(),
            system_platform=platform.platform(),
            arena="A",
            code_directory=None,
            mode=RobotMode.DEV,
            zone=0,
        )

    astoria_version: str
    python_version: str
    system_platform: str

    arena: str
    code_directory: Optional[Path]
    mode: RobotMode
    zone: int
