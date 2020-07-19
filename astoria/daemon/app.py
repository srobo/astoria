"""Astoria HTTP API."""

from fastapi import FastAPI
from pydantic import BaseModel

from astoria import __version__
from astoria.common.metadata import SystemMetadata

app = FastAPI()


class DaemonInfo(BaseModel):
    """Information about the daemon."""

    version: str = __version__
    name: str = "Astoria Daemon"
    code_status: str = "UNKNOWN"


@app.get('/', response_model=DaemonInfo)
async def daemon_info() -> DaemonInfo:
    """Get information about the running daemon."""
    return DaemonInfo()


@app.get('/metadata', response_model=SystemMetadata)
async def system_metadata() -> SystemMetadata:
    """
    Get the current system metadata.

    This is the data that should be provided to users.
    """
    return SystemMetadata.init()
