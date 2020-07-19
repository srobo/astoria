"""Astoria HTTP API."""

from astoria.common.metadata import SystemMetadata

from .daemon import AstoriaDaemon
from .info import DaemonInfo

app = AstoriaDaemon()


@app.get('/', response_model=DaemonInfo)
async def daemon_info() -> DaemonInfo:
    """Get information about the running daemon."""
    return app.daemon_info


@app.get('/metadata', response_model=SystemMetadata)
async def system_metadata() -> SystemMetadata:
    """
    Get the current system metadata.

    This is the data that should be provided to users.
    """
    return app.system_metadata
