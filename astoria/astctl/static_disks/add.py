"""Command to add a filesystem path as a static disk."""

import asyncio
from pathlib import Path

import click
import uvloop

from astoria.astctl.command import Command
from astoria.common.ipc import AddStaticDiskRequest


@click.command("add")
@click.argument("path")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def add(path: str, *, verbose: bool, config_file: str | None) -> None:
    """Mount a filesystem path as a disk."""
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        command = AddStaticDiskCommand(path, verbose, config_file)
        runner.run(command.run())


class AddStaticDiskCommand(Command):
    """Command to add a filesystem path as a static disk."""

    _path: Path

    dependencies = ["astdiskd"]

    def __init__(
        self,
        path: str,
        verbose: bool,  # noqa: FBT001
        config_file: str | None,
    ) -> None:
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
