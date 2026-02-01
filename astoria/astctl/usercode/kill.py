"""Command to restart running usercode."""

import click

from astoria.astctl.command import Command
from astoria.common.ipc import ManagerRequest


@click.command("kill")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def kill(*, verbose: bool, config_file: str | None) -> None:
    """Kill running usercode."""
    KillUsercodeCommand(verbose, config_file).execute()


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
