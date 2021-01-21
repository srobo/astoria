"""Command to display astoria events."""
import asyncio
from json import JSONDecodeError, loads
from pathlib import Path
from pprint import pprint
from typing import IO, Match

import click

from astoria.common.consumer import StateConsumer

loop = asyncio.get_event_loop()


@click.command("event")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.File('r'), default=Path("astoria.toml"))
@click.option("--json", type=bool, is_flag=True, default=False)
def event(*, verbose: bool, config_file: IO[str], json: bool) -> None:
    """Show Astoria events in real time."""
    command = EventCommand(verbose, config_file, json)
    loop.run_until_complete(command.run())


class EventCommand(StateConsumer):
    """Command to display astoria events."""

    name_prefix = "astctl"

    def __init__(self, verbose: bool, config_file: IO[str], json: bool) -> None:
        super().__init__(verbose, config_file)
        self._json = json

    def _init(self) -> None:
        """Initialise consumer."""
        self._mqtt.subscribe("+", self.handle_message)

    async def main(self) -> None:
        """Main method of the command."""
        await self.wait_loop()

    async def handle_message(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """Handle state manager status messages."""
        if self._json:
            data = {
                "topic": match.group(0),
                "payload": payload,
            }
            print(data)
        else:
            print("Received message from " + match.group(0))
            try:
                pprint(loads(payload))
            except JSONDecodeError:
                print("Could not decode JSON data.")
