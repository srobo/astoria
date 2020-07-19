"""DaemonInfo struct."""
from pydantic import BaseModel

from astoria import __version__


class DaemonInfo(BaseModel):
    """Information about the daemon."""

    @classmethod
    def init(cls) -> 'DaemonInfo':
        """Initialise da"""
        return cls(
            version=__version__,
            name="Astoria Daemon",
            code_status="UNKNOWN",
        )

    version: str
    name: str
    code_status: str
