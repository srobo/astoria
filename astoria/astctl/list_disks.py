"""Command to list information about mounted disks."""
import asyncio
from typing import Optional

import click

from astoria.common.ipc import DiskManagerMessage

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
        disks = message.calculate_disk_info(
            self.config.astprocd.default_usercode_entrypoint,
        )
        for uuid, disk in disks.items():
            print(f"\tUUID: {uuid}")
            print(f"\t\tMounted at: {disk.mount_path}")
            print(f"\t\tDisk Type: {disk.disk_type.name}")
