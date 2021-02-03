"""Command to restart running usercode."""
import asyncio
from typing import Optional

import click

from astoria.common.consumer import StateConsumer
from astoria.common.manager_requests import ManagerRequest

loop = asyncio.get_event_loop()


@click.command("kill")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def kill(*, verbose: bool, config_file: Optional[str]) -> None:
    """Kill running usercode."""
    command = KillUsercodeCommand(verbose, config_file)
    loop.run_until_complete(command.run())


class KillUsercodeCommand(StateConsumer):
    """Kill running usercode."""

    name_prefix = "astctl"
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
