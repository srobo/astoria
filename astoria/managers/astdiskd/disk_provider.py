"""A provider of disk information."""

from abc import ABCMeta
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Coroutine, Dict

from astoria.common.messages.astdiskd import DiskUUID

if TYPE_CHECKING:
    from .disk_manager import DiskManager


class DiskProvider(metaclass=ABCMeta):
    """
    A provider of disk information.

    Multiple disk providers can be used within one astdiskd process.
    """

    def __init__(
        self,
        disk_manager: 'DiskManager',
        *,
        notify_coro: Callable[[], Coroutine[None, None, None]],
    ) -> None:
        self._disk_manager = disk_manager
        self._notify_coro = notify_coro

        self._disks: Dict[DiskUUID, Path] = {}

    @property
    def disks(self) -> Dict[DiskUUID, Path]:
        """Currently mounted disks."""
        return self._disks

    async def main(self) -> None:
        """Main loop to detect disks if necessary."""
        pass
