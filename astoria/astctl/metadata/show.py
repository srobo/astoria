"""Command to show metadata."""
import asyncio
from typing import Optional

import click

from astoria.astctl.command import SingleManagerMessageCommand
from astoria.common.ipc import MetadataManagerMessage

loop = asyncio.get_event_loop()


@click.command("show")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def show(*, verbose: bool, config_file: Optional[str]) -> None:
    """Show current metadata."""
    command = ShowMetadataCommand(verbose, config_file)
    loop.run_until_complete(command.run())


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
