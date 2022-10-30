"""States that running code can be in."""
from enum import Enum


class CodeStatus(str, Enum):
    """Status of the running code."""

    STARTING = "code_starting"
    RUNNING = "code_running"
    KILLED = "code_killed"
    FINISHED = "code_finished"
    CRASHED = "code_crashed"
