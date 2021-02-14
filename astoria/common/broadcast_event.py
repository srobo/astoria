"""Broadcast Event Schemas."""
from typing import Dict, Type

from pydantic import BaseModel


class BroadcastEvent(BaseModel):
    """Schema for a broadcast event."""

    event_name: str
    sender_name: str
    priority: int = 0

    def __gt__(self, other: 'BroadcastEvent') -> bool:
        return self.priority > other.priority


class UsercodeLogBroadcastEvent(BroadcastEvent):
    """
    Schema for a log event from a usercode process.

    The priority of the event should be used to order the lines of the log.
    The pid should be used to differentiate between code runs.
    Content should be a single log line from the process, without a new line.
    """

    pid: int
    content: str


EVENTS: Dict[str, Type[BroadcastEvent]] = {
    "start_button": BroadcastEvent,
    "usercode_log": UsercodeLogBroadcastEvent,
}
