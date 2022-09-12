"""Rauc Update Manager Application."""

import asyncio
import logging

from astoria.common.components import StateManager
from astoria.common.ipc import RaucUpdateManagerMessage

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class RaucUpdateManager(StateManager[RaucUpdateManagerMessage]):
    """Astoria Rauc Update State Manager."""

    name = "astraucd"
    dependencies = ["astdiskd"]

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
        await self.wait_loop()
