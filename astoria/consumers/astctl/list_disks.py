"""Command to list information about mounted disks."""
import asyncio
from typing import Optional

import click

from astoria.common.messages.astdiskd import DiskManagerMessage

from .command import SingleManagerMessageCommand

loop = asyncio.get_event_loop()


@click.command("list-disks")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def list_disks(*, verbose: bool, config_file: Optional[str]) -> None:
    """List information about mounted disks."""
    command = ListDisksCommand(verbose, config_file)
    loop.run_until_complete(command.run())


class ListDisksCommand(SingleManagerMessageCommand[DiskManagerMessage]):
    """List disk information."""

    manager = "astdiskd"
    message_schema = DiskManagerMessage

    def handle_message(
        self,
        message: DiskManagerMessage,
    ) -> None:
        """Display information about the disks."""
        print(f"{len(message.disks)} disks found")
        for uuid, disk in message.disks.items():
            print(f"\tUUID: {uuid}")
            print(f"\t\tMounted at: {disk.mount_path}")
            print(f"\t\tDisk Type: {disk.disk_type.name}")
