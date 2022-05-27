"""StateManager to manage disks."""
import asyncio
import logging
from pathlib import Path
from typing import List

from astoria.common.components import StateManager
from astoria.common.ipc import DiskManagerMessage

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

        # Send a disk manager update on startup so we don't wait for the first disk.
        await self.update_state()

        # Wait whilst the program is running.
        await self.wait_loop()

    async def update_state(self) -> None:
        """Update the status of astdiskd when disks are changed."""
        disks = {}
        for provider in self._providers:
            for uuid, mount_path in provider.disks.items():
                # Only add the disk if it's not ignored.
                if mount_path not in self.config.astdiskd.ignored_mounts:
                    disks[uuid] = mount_path
                else:
                    LOGGER.info(f"Ignoring {mount_path} as it is an ignored mount.")

        self.status = DiskManagerMessage(
            status=DiskManagerMessage.Status.RUNNING,
            disks=disks,
        )
