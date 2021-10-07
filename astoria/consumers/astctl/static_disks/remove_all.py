"""Command to add a filesystem path as a static disk."""
import asyncio
from typing import Optional

import click

from astoria.common.manager_requests import RemoveAllStaticDisksRequest
from astoria.consumers.astctl.command import Command

loop = asyncio.get_event_loop()


@click.command("remove-all")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def remove_all(*, verbose: bool, config_file: Optional[str]) -> None:
    """Unmount all currently mounted static disks."""
    command = RemoveAllStaticDiskCommand(verbose, config_file)
    loop.run_until_complete(command.run())


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
