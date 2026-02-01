"""Command to virtually press start button."""

import click

from astoria.astctl.command import Command
from astoria.common.ipc import StartButtonBroadcastEvent
from astoria.common.mqtt import BroadcastHelper


@click.command("trigger")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def trigger(*, verbose: bool, config_file: str | None) -> None:
    """Virtually trigger the start button."""
    TriggerUsercodeCommand(verbose, config_file).execute()


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
