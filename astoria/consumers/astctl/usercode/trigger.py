"""Command to virtually press start button."""
import asyncio
from typing import Optional

import click

from astoria.common.broadcast_event import StartButtonBroadcastEvent
from astoria.common.mqtt import BroadcastHelper
from astoria.consumers.astctl.command import Command

loop = asyncio.get_event_loop()


@click.command("trigger")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def trigger(*, verbose: bool, config_file: Optional[str]) -> None:
    """Virtually trigger the start button."""
    command = TriggerUsercodeCommand(verbose, config_file)
    loop.run_until_complete(command.run())


class TriggerUsercodeCommand(Command):
    """Virtually trigger the start button."""

    def _init(self) -> None:
        """
        Initialisation of the data component.

        Called in the constructor of the parent class.
        """
        self._trigger_event = BroadcastHelper.get_helper(
            self._mqtt,
            StartButtonBroadcastEvent,
        )

    async def main(self) -> None:
        """Send a trigger event."""
        self._trigger_event.send()
