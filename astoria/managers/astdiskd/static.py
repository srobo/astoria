import logging
from typing import Callable, Coroutine, TYPE_CHECKING

from astoria.common.manager_requests import AddStaticDiskRequest, RequestResponse

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

    async def handle_add_static_disk(
        self,
        request: AddStaticDiskRequest,
    ) -> RequestResponse:
        if request.path.exists() and request.path.is_dir():
            if request.path in self.disks.values():
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
