"""Command to view usercode logs in real-time."""

import asyncio

import click
import uvloop

from astoria.astctl.command import Command
from astoria.common.ipc import UsercodeLogBroadcastEvent
from astoria.common.mqtt import BroadcastHelper


@click.command("log")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def log(*, verbose: bool, config_file: str | None) -> None:
    """View usercode logs in real-time."""
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        command = ViewUsercodeLogCommand(verbose, config_file)
        runner.run(command.run())


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
        while not self._stop_event.is_set():
            # wait_broadcast waits forever until a broadcast, so we will use a short
            # timeout to ensure that the loop condition is checked.
            try:
                ev = await asyncio.wait_for(
                    self._log_event.wait_broadcast(),
                    timeout=0.1,
                )
                print(ev.content.rstrip())
            except TimeoutError:
                pass
