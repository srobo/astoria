import logging
from typing import Callable, Coroutine, TYPE_CHECKING

from astoria.common.manager_requests import AddStaticDiskRequest, RemoveAllStaticDisksRequest, RemoveStaticDiskRequest, \
    RequestResponse

from .disk_provider import DiskProvider

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from . import DiskManager

class StaticDiskProvider(DiskProvider):

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
        if request.path.exists() and request.path.is_dir():
            if request.path in [str(disk_path) for disk_path in self.disks.values()]:
                return RequestResponse(
                    uuid=request.uuid,
                    success=False,
                    reason=f"The specified path is already mounted.",
                )

            self.disks[f"static-{request.uuid}"] = request.path
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
        removed = False
        for uuid, path in self.disks.items():
            LOGGER.info(uuid)
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
