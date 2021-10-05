"""Command to add a filesystem path as a static disk."""
import asyncio
from pathlib import Path
from typing import Optional

import click

from astoria.common.manager_requests import AddStaticDiskRequest
from astoria.consumers.astctl.command import Command

loop = asyncio.get_event_loop()


@click.command("add")
@click.argument("path")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def add(path: str, *, verbose: bool, config_file: Optional[str]) -> None:
    """Mount a filesystem path as a disk."""
    command = AddStaticDiskCommand(path, verbose, config_file)
    loop.run_until_complete(command.run())


class AddStaticDiskCommand(Command):
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
            "add_static_disk",
            AddStaticDiskRequest(sender_name=self.name, path=self._path),
        )
        if res.success:
            print("Successfully added disk.")
            if len(res.reason) > 0:
                print(res.reason)
        else:
            print("Unable to add disk.")
            if len(res.reason) > 0:
                print(res.reason)
        # Add timeout
        self.halt(silent=True)
