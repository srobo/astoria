"""Command to show metadata."""
import asyncio
from json import JSONDecodeError, loads
from pathlib import Path
from typing import IO, Match

import click

from astoria.common.consumer import StateConsumer
from astoria.common.messages.astmetad import MetadataManagerMessage

loop = asyncio.get_event_loop()


@click.command("metadata")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.File('r'), default=Path("astoria.toml"))
def show_metadata(*, verbose: bool, config_file: IO[str]) -> None:
    """Show current metadata."""
    command = ShowMetadataCommand(verbose, config_file)
    loop.run_until_complete(command.run())


class ShowMetadataCommand(StateConsumer):
    """Show current metadata."""

    name_prefix = "astctl"

    def _init(self) -> None:
        """Initialise consumer."""
        self._mqtt.subscribe("astmetad", self.handle_message)

    async def main(self) -> None:
        """Main method of the command."""
        await self.wait_loop()

    async def handle_message(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """Handle astmetad status messages."""
        try:
            message = MetadataManagerMessage(**loads(payload))
            if message.status == MetadataManagerMessage.Status.RUNNING:
                for i, v in message.metadata.__dict__.items():
                    print(f"{i}: {v}")
            else:
                print("astmetad is not running")
        except JSONDecodeError:
            print("Could not decode JSON data.")
        self.halt(silent=True)
