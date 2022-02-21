"""Command to show usercode info."""
import asyncio
from typing import Optional

import click

from astoria.astctl.command import SingleManagerMessageCommand
from astoria.common.ipc import ProcessManagerMessage

loop = asyncio.get_event_loop()


@click.command("show")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def show(*, verbose: bool, config_file: Optional[str]) -> None:
    """Show current usercode."""
    command = ShowUsercodeCommand(verbose, config_file)
    loop.run_until_complete(command.run())


class ShowUsercodeCommand(SingleManagerMessageCommand[ProcessManagerMessage]):
    """Show current usercode."""

    manager = "astprocd"
    message_schema = ProcessManagerMessage

    def handle_message(
        self,
        message: ProcessManagerMessage,
    ) -> None:
        """Print the process status."""
        if message.code_status is not None and message.disk_info is not None:
            print(f"Code status: {message.code_status.value}")
            print(f"Disk Mountpoint: {message.disk_info.mount_path}")
        else:
            print("No usercode disk is inserted.")
