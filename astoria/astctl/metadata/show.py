"""Command to show metadata."""
import asyncio
from typing import Optional

import click
import uvloop

from astoria.astctl.command import SingleManagerMessageCommand
from astoria.common.ipc import MetadataManagerMessage


@click.command("show")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def show(*, verbose: bool, config_file: Optional[str]) -> None:
    """Show current metadata."""
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        command = ShowMetadataCommand(verbose, config_file)
        runner.run(command.run())


class ShowMetadataCommand(SingleManagerMessageCommand[MetadataManagerMessage]):
    """Show current metadata."""

    manager = "astmetad"
    message_schema = MetadataManagerMessage

    def handle_message(
        self,
        message: MetadataManagerMessage,
    ) -> None:
        """Print the metadata."""
        print("Current Astoria Metadata is:")
        for i, v in sorted(message.metadata.__dict__.items()):
            print(f"\t{i}: {v}")
