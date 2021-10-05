"""Command to add a filesystem path as a static disk."""
import asyncio
from pathlib import Path
from typing import Optional

import click

from astoria.common.manager_requests import RemoveStaticDiskRequest
from astoria.consumers.astctl.command import Command

loop = asyncio.get_event_loop()


@click.command("remove")
@click.argument("path")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def remove(path: str, *, verbose: bool, config_file: Optional[str]) -> None:
    """Unmount a static disk."""
    command = RemoveStaticDiskCommand(path, verbose, config_file)
    loop.run_until_complete(command.run())


class RemoveStaticDiskCommand(Command):
    """Command to add a filesystem path as a static disk."""

    _path: Path

    dependencies = ["astdiskd"]

    def __init__(
        self,
        path: str,
        verbose: bool,
        config_file: Optional[str],
    ):
        super().__init__(verbose, config_file)
        self._path = Path(path).resolve()

    async def main(self) -> None:
        """Main method of the command."""
        res = await self._mqtt.manager_request(
            "astdiskd",
            "remove_static_disk",
            RemoveStaticDiskRequest(sender_name=self.name, path=self._path),
        )
        if res.success:
            print("Successfully removed disk.")
            if len(res.reason) > 0:
                print(res.reason)
        else:
            print("Unable to remove disk.")
            if len(res.reason) > 0:
                print(res.reason)
        # Add timeout
        self.halt(silent=True)
