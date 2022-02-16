"""Command to restart running usercode."""
import asyncio
from typing import Optional

import click

from astoria.astctl.command import Command
from astoria.common.ipc import ManagerRequest

loop = asyncio.get_event_loop()


@click.command("restart")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def restart(*, verbose: bool, config_file: Optional[str]) -> None:
    """Restart running usercode."""
    command = RestartUsercodeCommand(verbose, config_file)
    loop.run_until_complete(command.run())


class RestartUsercodeCommand(Command):
    """Restart running usercode."""

    dependencies = ["astprocd"]

    async def main(self) -> None:
        """Main method of the command."""
        res = await self._mqtt.manager_request(
            "astprocd",
            "restart",
            ManagerRequest(sender_name=self.name),
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
