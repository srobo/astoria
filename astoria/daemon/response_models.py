"""API Response models."""
import platform

from pydantic import BaseModel

from astoria import __version__


class DaemonInfo(BaseModel):
    """Information about the daemon."""

    version: str = __version__
    name: str = "Astoria Daemon"
    code_status: str = "UNKNOWN"


class SystemMetadata(BaseModel):
    """The current metadata."""

    astoria_version: str = __version__
    python_version: str = platform.python_version()
    system_platform: str = platform.platform()