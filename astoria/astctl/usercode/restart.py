"""Command to restart running usercode."""

import click

from astoria.astctl.command import Command
from astoria.common.ipc import ManagerRequest


@click.command("restart")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def restart(*, verbose: bool, config_file: str | None) -> None:
    """Restart running usercode."""
    RestartUsercodeCommand(verbose, config_file).execute()


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
