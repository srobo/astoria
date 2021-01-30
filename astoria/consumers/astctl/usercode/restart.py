"""Command to restart running usercode."""
import asyncio
from pathlib import Path
from typing import IO

import click

from astoria.common.consumer import StateConsumer
from astoria.common.mutation_requests import MutationRequest

loop = asyncio.get_event_loop()


@click.command("restart")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.File('r'), default=Path("astoria.toml"))
def restart(*, verbose: bool, config_file: IO[str]) -> None:
    """Restart running usercode."""
    command = RestartUsercodeCommand(verbose, config_file)
    loop.run_until_complete(command.run())


class RestartUsercodeCommand(StateConsumer):
    """Restart running usercode."""

    name_prefix = "astctl"
    dependencies = ["astprocd"]

    async def main(self) -> None:
        """Main method of the command."""
        res = await self._mqtt.mutation_request(
            "astprocd",
            "restart",
            MutationRequest(sender_name=self.name),
        )
        if res.success:
            print("Successfully restarted code.")
            if len(res.reason) > 0:
                print(res.reason)
        else:
            print("Unable to restart code.")
            if len(res.reason) > 0:
                print(res.reason)
        # Add timeout
        self.halt(silent=True)
