"""StateManager to manage disks."""
import asyncio
import logging

from astoria.common.manager import StateManager
from astoria.common.messages.astdiskd import (
    DiskInfo,
    DiskManagerMessage,
    DiskType,
)

from .udisks import UdisksConnection

LOGGER = logging.getLogger(__name__)


class DiskManager(StateManager[DiskManagerMessage]):
    """Astoria Disk Manager."""

    name = "astdiskd"

    def _init(self) -> None:
        self._udisks = UdisksConnection(notify_coro=self.update_state)

    @property
    def offline_status(self) -> DiskManagerMessage:
        """
        Status to publish when the manager goes offline.

        This status should ensure that any other components relying
        on this data go into a safe state.
        """
        return DiskManagerMessage(
            status=DiskManagerMessage.Status.STOPPED,
            disks={},
        )

    async def main(self) -> None:
        """Main routine for astdiskd."""
        asyncio.ensure_future(self._udisks.main())

        # Wait whilst the program is running.
        await self.wait_loop()

    async def update_state(self) -> None:
        """Update the status of astdiskd when disks are changed."""
        disks = {}
        for uuid, mount_path in self._udisks.disks.items():
            disks[uuid] = DiskInfo(
                uuid=uuid,
                mount_path=mount_path,
                disk_type=DiskType.determine_disk_type(mount_path),
            )
        self.status = DiskManagerMessage(
            status=DiskManagerMessage.Status.RUNNING,
            disks=disks,
        )
