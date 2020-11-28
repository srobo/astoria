"""astprocd - Astoria Process Manager."""

import asyncio
import logging
from json import loads
from pathlib import Path
from typing import IO, Dict, Match

import click
import gmqtt

from astoria.common.manager import StateManager
from astoria.common.messages.astdiskd import (
    DiskInfoMessage,
    DiskManagerStatusMessage,
    DiskUUID,
)
from astoria.common.messages.astprocd import ProcessManagerStatusMessage
from astoria.common.mqtt import Registry

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()

registry = Registry()


@click.command("astprocd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.File('r'), default=Path("astoria.toml"))
def main(*, verbose: bool, config_file: IO[str]) -> None:
    """Process Manager."""
    procd = ProcessManager(verbose, config_file, registry)
    loop.run_until_complete(procd.run())


class ProcessManager(StateManager):
    """Astoria Process Manager."""

    name = "astprocd"
    dependencies = ["astdiskd"]

    def _init(self) -> None:
        self._cur_disks: Dict[DiskUUID, DiskInfoMessage] = {}

    @property
    def last_will_message(self) -> gmqtt.Message:
        """The MQTT last will and testament."""
        return gmqtt.Message(
            f"{self.mqtt_prefix}/status",
            ProcessManagerStatusMessage(
                status=ProcessManagerStatusMessage.ManagerStatus.STOPPED,
            ).json(),
            retain=True,
        )

    @registry.handler('astoria/astdiskd/status')
    async def handle_astdiskd_status_message(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """Handle astdiskd status messages."""
        info = DiskManagerStatusMessage(**loads(payload))
        if info.status is DiskManagerStatusMessage.ManagerStatus.STOPPED:
            LOGGER.warning("astdiskd is not running!")
        else:
            LOGGER.info("Successfully synced with astdiskd")

    @registry.handler('astoria/astdiskd/disks/+')
    async def handle_astdiskd_disk_info_message(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """Handle disk info messages."""
        uuid = DiskUUID(match.group(1))
        if payload:
            if uuid not in self._cur_disks:
                info = DiskInfoMessage(**loads(payload))
                self._cur_disks[uuid] = info
        else:
            info = self._cur_disks.pop(uuid)

    async def main(self) -> None:
        """Main routine for astprocd."""
        # Wait whilst the program is running.
        await self.wait_loop()
