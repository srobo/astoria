"""Stubs for systemd.daemon."""

from typing import List, Optional

def notify(
        status: str,
        unset_environment: bool = False,
        pid: int = 0,
        fds: Optional[List[int]] = None
) -> bool:
    """
    Notify the systemd process.

    Send a message to the init system about a status change.

    Wraps sd_notify(3)
    """
    ...