"""Mixin to handle metadata."""
import logging
from json import JSONDecodeError, loads
from typing import Match

from pydantic import ValidationError, parse_obj_as

from astoria.common.config import AstoriaConfig
from astoria.common.ipc import MetadataManagerMessage
from astoria.common.metadata import Metadata

LOGGER = logging.getLogger(__name__)


class MetadataHandlerMixin:
    """Mixin to parse metadata updates."""

    config: AstoriaConfig

    async def handle_astmetad_message(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """Event handler for metadata changes."""
        if payload:
            try:
                data = loads(payload)
                metadata_manager_message = parse_obj_as(MetadataManagerMessage, data)
                await self.handle_metadata(metadata_manager_message.metadata)
            except ValidationError:
                LOGGER.warning("Received bad metadata manager message.")
            except JSONDecodeError:
                LOGGER.warning("Received bad JSON in metadata manager message.")
        else:
            LOGGER.warning("Received empty metadata manager message.")

    async def handle_metadata(self, metadata: Metadata) -> None:
        """
        Handle the updated metadata.

        :param metadata: The metadata included in the update.
        """
        LOGGER.debug(f"Received new metadata: {metadata.json()}")
