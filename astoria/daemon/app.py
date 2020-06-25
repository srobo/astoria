"""Astoria HTTP API."""

from fastapi import FastAPI

from .response_models import DaemonInfo, SystemMetadata

app = FastAPI()


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
    return SystemMetadata()
