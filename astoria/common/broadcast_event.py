"""Broadcast Event Schemas."""
from enum import Enum
from typing import ClassVar

from pydantic import BaseModel


class BroadcastEvent(BaseModel):
    """Schema for a broadcast event."""

    name: ClassVar[str]

    event_name: str
    sender_name: str
    priority: int = 0

    def __gt__(self, other: 'BroadcastEvent') -> bool:
        return self.priority > other.priority


class StartButtonBroadcastEvent(BroadcastEvent):
    """
    Schema for a remote start event.

    Trigger the robot code if it is waiting for the start button to be
    pressed. Does not affect or interact with the physical button as that
    is handled by the usercode driver.
    """

    name: ClassVar[str] = "start_button"


class LogEventSource(Enum):
    """The source of a line of log output."""

    ASTORIA = "astoria"
    STDOUT = "stdout"
    STDERR = "stderr"


class UsercodeLogBroadcastEvent(BroadcastEvent):
    """
    Schema for a log event from a usercode process.

    The priority of the event should be used to order the lines of the log.
    The pid should be used to differentiate between code runs.
    Content should be a single log line from the process, without a new line.
    """

    name: ClassVar[str] = "usercode_log"

    pid: int
    content: str
    source: LogEventSource
