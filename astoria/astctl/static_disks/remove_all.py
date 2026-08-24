"""Command to add a filesystem path as a static disk."""

import click

from astoria.astctl.command import Command
from astoria.common.ipc import RemoveAllStaticDisksRequest


@click.command("remove-all")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def remove_all(*, verbose: bool, config_file: str | None) -> None:
    """Unmount all currently mounted static disks."""
    RemoveAllStaticDiskCommand(verbose, config_file).execute()


class RemoveAllStaticDiskCommand(Command):
    """Command to add a filesystem path as a static disk."""

    dependencies = ["astdiskd"]

    async def main(self) -> None:
        """Main method of the command."""
        res = await self._mqtt.manager_request(
            "astdiskd",
            "remove_all_static_disks",
            RemoveAllStaticDisksRequest(sender_name=self.name),
        )
        if res.success:
            if len(res.reason) > 0:
                print(res.reason)
        else:
            if len(res.reason) > 0:
                print(res.reason)
        # Add timeout
        self.halt(silent=True)
