"""Command to view usercode logs in real-time."""
import asyncio
import signal
from typing import Optional

import click

from astoria.common.broadcast_event import UsercodeLogBroadcastEvent
from astoria.common.mqtt import BroadcastHelper
from astoria.consumers.astctl.command import Command

loop = asyncio.get_event_loop()


@click.command("log")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def log(*, verbose: bool, config_file: Optional[str]) -> None:
    """View usercode logs in real-time."""
    command = ViewUsercodeLogCommand(verbose, config_file)
    loop.run_until_complete(command.run())


class ViewUsercodeLogCommand(Command):
    """Command to view usercode logs in real-time."""

    def _init(self) -> None:
        """
        Initialisation of the data component.

        Called in the constructor of the parent class.
        """
        self._log_event = BroadcastHelper.get_helper(
            self._mqtt,
            UsercodeLogBroadcastEvent,
        )

    async def main(self) -> None:
        """Send a trigger event."""
        signal.signal(signal.SIGINT, self._exit)
        while True:
            ev = await self._log_event.wait_broadcast()
            print(ev)
