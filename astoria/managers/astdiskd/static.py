"""Allows disks to be added manually through local filesystem paths."""
import logging
from typing import TYPE_CHECKING, Callable, Coroutine

from astoria.common.manager_requests import (
    AddStaticDiskRequest,
    RemoveAllStaticDisksRequest,
    RemoveStaticDiskRequest,
    RequestResponse,
)
from astoria.common.messages.astdiskd import DiskUUID

from .disk_provider import DiskProvider

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .disk_manager import DiskManager


class StaticDiskProvider(DiskProvider):
    """Provides disks added manually via a command."""

    def __init__(
        self,
        disk_manager: 'DiskManager',
        *,
        notify_coro: Callable[[], Coroutine[None, None, None]],
    ) -> None:
        super().__init__(disk_manager, notify_coro=notify_coro)
        self._disk_manager._register_request(
            "add_static_disk",
            AddStaticDiskRequest,
            self.handle_add_static_disk,
        )
        self._disk_manager._register_request(
            "remove_static_disk",
            RemoveStaticDiskRequest,
            self.handle_remove_static_disk,
        )
        self._disk_manager._register_request(
            "remove_all_static_disks",
            RemoveAllStaticDisksRequest,
            self.handle_remove_all_static_disks,
        )

    async def handle_add_static_disk(
        self,
        request: AddStaticDiskRequest,
    ) -> RequestResponse:
        """Handles the add static disk command."""
        if request.path.exists() and request.path.is_dir():
            if str(request.path) in map(lambda d: str(d), self.disks.values()):
                return RequestResponse(
                    uuid=request.uuid,
                    success=False,
                    reason="The specified path is already mounted.",
                )

            self.disks[DiskUUID(f"static-{request.uuid}")] = request.path
            await self._notify_coro()
            LOGGER.info(f"Static disk {request.uuid} mounted ({request.path})")
            return RequestResponse(
                uuid=request.uuid,
                success=True,
            )
        else:
            return RequestResponse(
                uuid=request.uuid,
                success=False,
                reason=f"{request.path} does not exist or is not a directory",
            )

    async def handle_remove_static_disk(
        self,
        request: RemoveStaticDiskRequest,
    ) -> RequestResponse:
        """Handles the remove static disk command."""
        if request.path in self.disks.values():
            for uuid, path in self.disks.items():
                if str(path) == str(request.path):
                    del self.disks[uuid]
                    LOGGER.info(f'Static disk {uuid} unmounted ({request.path})')
                    return RequestResponse(
                        uuid=request.uuid,
                        success=True,
                    )
            return RequestResponse(
                uuid=request.uuid,
                success=False,
                reason="Could not remove static disk.",
            )
        else:
            return RequestResponse(
                uuid=request.uuid,
                success=False,
                reason=f"{request.path} is not mounted as a static disk.",
            )

    async def handle_remove_all_static_disks(
        self,
        request: RemoveAllStaticDisksRequest,
    ) -> RequestResponse:
        """Handles the remove all static disks command."""
        removed = False
        for uuid, path in self.disks.items():
            if uuid.startswith('static-'):
                removed = True
                del self.disks[uuid]
                LOGGER.info(f'Static disk {uuid} unmounted ({path})')

        if not removed:
            return RequestResponse(
                uuid=request.uuid,
                success=True,
                reason='There are no static disks to remove.',
            )

        return RequestResponse(
            uuid=request.uuid,
            success=True,
            reason='Successfully removed all static disks.',
        )
