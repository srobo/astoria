"""Command to list information about mounted disks."""
import asyncio
from json import JSONDecodeError, loads
from pathlib import Path
from typing import IO, Match

import click

from astoria.common.consumer import StateConsumer
from astoria.common.messages.astdiskd import DiskManagerMessage

loop = asyncio.get_event_loop()


@click.command("list-disks")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.File('r'), default=Path("astoria.toml"))
def list_disks(*, verbose: bool, config_file: IO[str]) -> None:
    """List information about mounted disks."""
    command = ListDisksCommand(verbose, config_file)
    loop.run_until_complete(command.run())


class ListDisksCommand(StateConsumer):
    """List disk information."""

    name_prefix = "astctl"

    def _init(self) -> None:
        """Initialise consumer."""
        self._mqtt.subscribe("astdiskd", self.handle_message)

    async def main(self) -> None:
        """Main method of the command."""
        await self.wait_loop()

    async def handle_message(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """Handle astdiskd status messages."""
        try:
            message = DiskManagerMessage(**loads(payload))
            if message.status == DiskManagerMessage.Status.RUNNING:
                print(f"{len(message.disks)} disks found")
                for uuid, disk in message.disks.items():
                    print(f"\tUUID: {uuid}")
                    print(f"\t\tMounted at: {disk.mount_path}")
                    print(f"\t\tDisk Type: {disk.disk_type.name}")
            else:
                print("astdiskd is not running")
        except JSONDecodeError:
            print("Could not decode JSON data.")
        self.halt(silent=True)
