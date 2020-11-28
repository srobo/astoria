"""Message schemas for astprocd."""

from .base import BaseManagerStatusMessage


class ProcessManagerStatusMessage(BaseManagerStatusMessage):
    """Status Message for astprocd."""
