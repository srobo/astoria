"""Schema definitions for mutation requests."""
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MutationRequest(BaseModel):
    """Schema definition for a Mutation Request."""

    uuid: UUID = Field(default_factory=uuid4)
    sender_name: str  # client name of component that sent the request


class MutationResponse(BaseModel):
    """Schema definition for a Mutation Response."""

    uuid: UUID
    success: bool
    reason: Optional[str] = ""


class MetadataMutationRequest(MutationRequest):
    """Schema definition for a metadata mutation."""

    attr: str
    value: str


UsercodeKillMutationRequest = MutationRequest
UsercodeRestartMutationRequest = MutationRequest
