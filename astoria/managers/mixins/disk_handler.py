"""Disk Handler Mixin."""

import asyncio
import logging
from json import JSONDecodeError, loads
from typing import Dict, Match

from astoria.common.messages.astdiskd import (
    DiskInfo,
    DiskManagerMessage,
    DiskUUID,
)

LOGGER = logging.getLogger(__name__)


class DiskHandlerMixin:
    """Mixin to translate disk events into insertions and removals."""

    _cur_disks: Dict[DiskUUID, DiskInfo]

    async def handle_astdiskd_disk_info_message(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """Handle disk info messages."""
        if payload:
            try:
                message = DiskManagerMessage(**loads(payload))

                new_set = set(message.disks.keys())
                old_set = set(self._cur_disks.keys())

                added_disks = new_set - old_set
                removed_disks = old_set - new_set

                for uuid in removed_disks:
                    info = self._cur_disks.pop(uuid)
                    asyncio.ensure_future(self.handle_disk_removal(uuid, info))

                for uuid in added_disks:
                    info = message.disks[uuid]
                    self._cur_disks[uuid] = info
                    asyncio.ensure_future(self.handle_disk_insertion(uuid, info))
            except JSONDecodeError:
                LOGGER.warning("Received bad JSON in disk manager message.")
        else:
            LOGGER.warning("Received empty disk manager message.")

    async def handle_disk_insertion(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        """Handle a disk insertion."""
        LOGGER.debug(f"Disk inserted: {uuid} ({disk_info.disk_type})")  # pragma: nocover

    async def handle_disk_removal(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        """Handle a disk removal."""
        LOGGER.debug(f"Disk removed: {uuid} ({disk_info.disk_type})")  # pragma: nocover
