"""StateManager to manage disks."""
import asyncio
import logging
from pathlib import Path
from typing import List

from astoria.common.manager import StateManager
from astoria.common.messages.astdiskd import (
    DiskInfo,
    DiskManagerMessage,
    DiskType,
)

from .disk_provider import DiskProvider
from .static import StaticDiskProvider
from .udisks import UdisksConnection

LOGGER = logging.getLogger(__name__)


class DiskManager(StateManager[DiskManagerMessage]):
    """Astoria Disk Manager."""

    name = "astdiskd"

    def _init(self) -> None:
        self._providers: List[DiskProvider] = [
            StaticDiskProvider(self, notify_coro=self.update_state),
        ]

        # Add UDisks provider if it DBus is installed
        if Path("/usr/bin/dbus-daemon").exists():
            self._providers.append(UdisksConnection(self, notify_coro=self.update_state))

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
        for provider in self._providers:
            asyncio.ensure_future(provider.main())

        # Wait whilst the program is running.
        await self.wait_loop()

    async def update_state(self) -> None:
        """Update the status of astdiskd when disks are changed."""
        disks = {}
        for provider in self._providers:
            for uuid, mount_path in provider.disks.items():
                disks[uuid] = DiskInfo(
                    uuid=uuid,
                    mount_path=mount_path,
                    disk_type=DiskType.determine_disk_type(mount_path),
                )
        self.status = DiskManagerMessage(
            status=DiskManagerMessage.Status.RUNNING,
            disks=disks,
        )
