"""Process Manager Application."""

import asyncio
import logging
from typing import Dict, Optional

from astoria.common.broadcast_event import UsercodeLogBroadcastEvent
from astoria.common.manager import StateManager
from astoria.common.manager_requests import (
    RequestResponse,
    UsercodeKillManagerRequest,
    UsercodeRestartManagerRequest,
)
from astoria.common.messages.astdiskd import DiskInfo, DiskType, DiskUUID
from astoria.common.messages.astprocd import CodeStatus, ProcessManagerMessage
from astoria.common.mqtt import BroadcastHelper
from astoria.managers.mixins.disk_handler import DiskHandlerMixin

from .usercode_lifecycle import UsercodeLifecycle

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class ProcessManager(DiskHandlerMixin, StateManager[ProcessManagerMessage]):
    """Astoria Process State Manager."""

    name = "astprocd"
    dependencies = ["astdiskd", "astmetad"]

    def _init(self) -> None:
        self._lifecycle: Optional[UsercodeLifecycle] = None
        self._cur_disks: Dict[DiskUUID, DiskInfo] = {}

        self._mqtt.subscribe("astdiskd", self.handle_astdiskd_disk_info_message)

        self._register_request(
            "restart",
            UsercodeRestartManagerRequest,
            self.handle_restart_request,
        )
        self._register_request(
            "kill",
            UsercodeKillManagerRequest,
            self.handle_kill_request,
        )
        self._log_helper = BroadcastHelper.get_helper(
            self._mqtt,
            UsercodeLogBroadcastEvent,
        )

    @property
    def offline_status(self) -> ProcessManagerMessage:
        """
        Status to publish when the manager goes offline.

        This status should ensure that any other components relying
        on this data go into a safe state.
        """
        return ProcessManagerMessage(
            status=ProcessManagerMessage.Status.STOPPED,
        )

    async def main(self) -> None:
        """Main routine for astprocd."""
        # Wait whilst the program is running.
        self.update_status()
        await self.wait_loop()

        for uuid, info in self._cur_disks.items():
            asyncio.ensure_future(self.handle_disk_removal(uuid, info))

    async def handle_disk_insertion(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        """Handle a disk insertion."""
        LOGGER.debug(f"Disk inserted: {uuid} ({disk_info.disk_type})")
        if disk_info.disk_type is DiskType.USERCODE:
            LOGGER.info(f"Usercode disk {uuid} is mounted at {disk_info.mount_path}")
            if self._lifecycle is None:
                LOGGER.debug(f"Starting usercode lifecycle for {uuid}")
                self._lifecycle = UsercodeLifecycle(
                    uuid,
                    disk_info,
                    self.update_status,
                    self._log_helper,
                    self.config,
                )
                asyncio.ensure_future(self._lifecycle.run_process())
            else:
                LOGGER.warn("Cannot run usercode, there is already a lifecycle present.")
                with disk_info.mount_path.joinpath("log.txt").open("w") as fh:
                    fh.write("Unable to start code.\n")
                    fh.write("It is not safe to run multiple code disks at once.\n")

    async def handle_disk_removal(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        """Handle a disk removal."""
        LOGGER.debug(f"Disk removed: {uuid} ({disk_info.disk_type})")

        if disk_info.disk_type is DiskType.USERCODE:
            LOGGER.info(f"Usercode disk {uuid} removed ({disk_info.mount_path})")

            if self._lifecycle is not None and self._lifecycle._uuid == disk_info.uuid:
                await self._lifecycle.kill_process()
                self._lifecycle = None
                self.update_status()
            else:
                LOGGER.warning("Disk removed, but no code lifecycle available")

    async def handle_kill_request(
            self,
            request: UsercodeKillManagerRequest,
    ) -> RequestResponse:
        """Handle a request to kill running usercode."""
        if self._lifecycle is None:
            return RequestResponse(
                uuid=request.uuid,
                success=False,
                reason="No active usercode lifecycle",
            )
        else:
            LOGGER.info("Kill request received.")
            await self._lifecycle.kill_process()
            return RequestResponse(
                uuid=request.uuid,
                success=True,
            )

    async def handle_restart_request(
        self,
        request: UsercodeRestartManagerRequest,
    ) -> RequestResponse:
        """Handle a request to restart usercode."""
        LOGGER.info("Restart request received.")
        if self._lifecycle is None:
            return RequestResponse(
                uuid=request.uuid,
                success=False,
                reason="No active usercode lifecycle",
            )
        else:
            if self._lifecycle.status is CodeStatus.RUNNING:
                return RequestResponse(
                    uuid=request.uuid,
                    success=False,
                    reason="Code is already running.",
                )
            else:
                asyncio.ensure_future(self._lifecycle.run_process())
                return RequestResponse(
                    uuid=request.uuid,
                    success=True,
                )

    def update_status(self, code_status: Optional[CodeStatus] = None) -> None:
        """
        Calculate and update the status of this manager.

        Called by the usercode lifecycle to inform us of changes.
        """
        if self._lifecycle is None:
            # When the status is updated in the lifecycle constructor, we
            # are left with a situation where there is no lifecycle object,
            # but the code is starting. Thus we want to inform anyway.
            #
            # This section also updates the status when the lifecycle is cleaned up.
            self.status = ProcessManagerMessage(
                status=ProcessManagerMessage.Status.RUNNING,
                code_status=code_status,
            )
        else:
            self.status = ProcessManagerMessage(
                status=ProcessManagerMessage.Status.RUNNING,
                code_status=self._lifecycle.status,
                disk_info=self._lifecycle.disk_info,
            )
