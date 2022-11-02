"""Schema definitions for manager requests."""
from pathlib import Path
from typing import final
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


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
