"""Astoria Daemon Class."""
from fastapi import FastAPI

from astoria.common.metadata import SystemMetadata

from .info import DaemonInfo


class AstoriaDaemon(FastAPI):
    """Astoria Daemon."""

    def __init__(self) -> None:
        super().__init__()

        self.daemon_info = DaemonInfo.init()
        self.system_metadata = SystemMetadata.init()
