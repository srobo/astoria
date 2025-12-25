"""Command to show usercode info."""

import asyncio

import click
import uvloop

from astoria.astctl.command import SingleManagerMessageCommand
from astoria.common.ipc import ProcessManagerMessage


@click.command("show")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def show(*, verbose: bool, config_file: str | None) -> None:
    """Show current usercode."""
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        command = ShowUsercodeCommand(verbose, config_file)
        runner.run(command.run())


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
