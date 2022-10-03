"""Schema definitions for manager requests."""
from pathlib import Path
from typing import Dict, Type, final
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RequestFailedException(RuntimeError):
    """A manager request failed to get a response."""


class ManagerRequest(BaseModel):
    """Schema definition for a Manager Request."""

    uuid: UUID = Field(default_factory=uuid4)
    sender_name: str  # client name of component that sent the request


@final
class RequestResponse(BaseModel):
    """Schema definition for the response to a Manager Request."""

    uuid: UUID
    success: bool
    reason: str = ""


class MetadataSetManagerRequest(ManagerRequest):
    """Schema definition for a metadata mutation."""

    attr: str
    value: str


UsercodeKillManagerRequest = ManagerRequest
UsercodeRestartManagerRequest = ManagerRequest


class AddStaticDiskRequest(ManagerRequest):
    """Schema definition for adding a static disk."""

    path: Path


class RemoveStaticDiskRequest(ManagerRequest):
    """Schema definition for removing a static disk."""

    path: Path


RemoveAllStaticDisksRequest = ManagerRequest

# Map of requests available on each state manager
# A request must be registered here to work.
REQUEST_TYPE_MAP: Dict[str, Dict[str, Type[ManagerRequest]]] = {
    "astdiskd": {
        "add_static_disk": AddStaticDiskRequest,
        "remove_static_disk": RemoveStaticDiskRequest,
        "remove_all_static_disks": RemoveAllStaticDisksRequest,
    },
    "astmetad": {
        "mutate": MetadataSetManagerRequest,
    },
    "astprocd": {
        "kill": UsercodeKillManagerRequest,
        "restart": UsercodeRestartManagerRequest,
    },
}
