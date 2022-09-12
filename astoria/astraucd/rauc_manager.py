"""Rauc Update Manager Application."""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from astoria.astraucd.update_lifecycle import UpdateLifecycle
from astoria.common.components import StateManager
from astoria.common.disks import DiskInfo, DiskUUID, DiskType
from astoria.common.ipc import RaucUpdateManagerMessage
from astoria.common.mixins import DiskHandlerMixin
from astoria.common.update_state import UpdateState

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class RaucUpdateManager(DiskHandlerMixin, StateManager[RaucUpdateManagerMessage]):
    """Astoria Rauc Update State Manager."""

    name = "astraucd"
    dependencies = ["astdiskd"]

    def _init(self) -> None:
        self._cur_disks = {}
        self._lifecycle: Optional[UpdateLifecycle] = None
        self._mqtt.subscribe("astdiskd", self.handle_astdiskd_disk_info_message)

    @property
    def offline_status(self) -> RaucUpdateManagerMessage:
        """
        Status to publish when the manager goes offline.

        This status should ensure that any other components relying
        on this data go into a safe state.
        """
        return RaucUpdateManagerMessage(
            status=RaucUpdateManagerMessage.Status.STOPPED,
        )

    async def main(self) -> None:
        """Main routine for astraucd."""
        if not self._lifecycle:
            self.update_status()
        await self.wait_loop()

    def _find_update_file(self, disk_info: DiskInfo) -> Path:
        return Path(__file__).resolve()  # TODO

    async def handle_disk_insertion(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        """Handle a disk insertion."""
        LOGGER.debug(f"Disk inserted: {uuid} ({disk_info.disk_type})")  # pragma: nocover
        if disk_info.disk_type is DiskType.UPDATE:
            LOGGER.info(f"Update disk {uuid} is mounted at {disk_info.mount_path}")
            if self._lifecycle is None:
                self._lifecycle = UpdateLifecycle(
                    self._find_update_file(disk_info),
                    self.update_status,
                )
                asyncio.ensure_future(self._lifecycle.run_process())
            else:
                LOGGER.warning("Multiple update disks have been inserted, ignoring all but the first.")

    def update_status(self, update_state: Optional[UpdateState] = None) -> None:
        """
        Calculate and update the status of this manager.

        Called by the update lifecycle to inform us of changes.
        """
        if self._lifecycle is None:
            # When the status is updated in the lifecycle constructor, we
            # are left with a situation where there is no lifecycle object,
            # but the code is starting. Thus we want to inform anyway.
            #
            # This section also updates the status when the lifecycle is cleaned up.
            self.status = RaucUpdateManagerMessage(
                status=RaucUpdateManagerMessage.Status.RUNNING,
            )
        else:
            self.status = RaucUpdateManagerMessage(
                status=RaucUpdateManagerMessage.Status.RUNNING,
                update_state=update_state,
            )
