"""A provider of disk information."""

from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import TYPE_CHECKING

from astoria.common.disks import DiskUUID

if TYPE_CHECKING:
    from .disk_manager import DiskManager


class DiskProvider:
    """
    A provider of disk information.

    Multiple disk providers can be used within one astdiskd process.
    """

    def __init__(
        self,
        disk_manager: "DiskManager",
        *,
        notify_coro: Callable[[], Coroutine[None, None, None]],
    ) -> None:
        self._disk_manager = disk_manager
        self._notify_coro = notify_coro

        self._disks: dict[DiskUUID, Path] = {}

    @property
    def disks(self) -> dict[DiskUUID, Path]:
        """Currently mounted disks."""
        return self._disks

    async def main(self) -> None:
        """Main loop to detect disks if necessary."""
        pass
