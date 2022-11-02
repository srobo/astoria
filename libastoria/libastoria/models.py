"""Data Models."""
from typing import List, TypeVar

from pydantic import BaseModel


class DataModel(BaseModel):
    """A data model for the API."""


DataT = TypeVar('DataT', bound=DataModel)


class DisksDomain(DataModel):
    """State held about mounted disks."""

    disks: List[str]


class ProcessDomain(DataModel):
    """State held about usercode processes."""

    running: bool


class LogMessage(DataModel):
    """A log message."""

    message: str = "yeet"
