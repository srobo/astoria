"""Command to restart running usercode."""
import asyncio
from typing import Optional

import click
import uvloop

from astoria.astctl.command import Command
from astoria.common.ipc import ManagerRequest


@click.command("kill")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def kill(*, verbose: bool, config_file: Optional[str]) -> None:
    """Kill running usercode."""
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        command = KillUsercodeCommand(verbose, config_file)
        runner.run(command.run())


class KillUsercodeCommand(Command):
    """Kill running usercode."""

    dependencies = ["astprocd"]

    async def main(self) -> None:
        """Main method of the command."""
        res = await self._mqtt.manager_request(
            "astprocd",
            "kill",
            ManagerRequest(sender_name=self.name),
        )
        if res.success:
            print("Successfully killed code.")
            if len(res.reason) > 0:
                print(res.reason)
        else:
            print("Unable to kill code.")
            if len(res.reason) > 0:
                print(res.reason)
        # Add timeout
        self.halt(silent=True)
