"""Stubs for systemd.journal."""

from typing import Optional

def send(
    MESSAGE: str,
    MESSAGE_ID: Optional[int] = None,
    CODE_FILE: Optional[str] = None,
    CODE_LINE: Optional[str] = None,
    CODE_FUNC: Optional[str] = None,
    SYSLOG_IDENTIFIER: Optional[str] = None,
    SYSLOG_PID: Optional[int] = None,
) -> None:
    """Send a message to the journal."""
    ...