"""Command to set a metadata attribute."""

import asyncio

import click
import uvloop

from astoria.astctl.command import Command
from astoria.common.ipc import MetadataSetManagerRequest


@click.command("set")
@click.argument("attribute")
@click.argument("value")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def set(  # noqa: A001
    attribute: str,
    value: str,
    *,
    verbose: bool,
    config_file: str | None,
) -> None:
    """Set a metadata attribute."""
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        command = SetMetadataCommand(attribute, value, verbose, config_file)
        runner.run(command.run())


class SetMetadataCommand(Command):
    """Set a metadata attribute."""

    dependencies = ["astmetad"]

    def __init__(
        self,
        attribute: str,
        value: str,
        verbose: bool,  # noqa: FBT001
        config_file: str | None,
    ) -> None:
        super().__init__(verbose, config_file)
        self._attr = attribute
        self._value = value

    async def main(self) -> None:
        """Main method of the command."""
        res = await self._mqtt.manager_request(
            "astmetad",
            "mutate",
            MetadataSetManagerRequest(
                sender_name=self.name,
                attr=self._attr,
                value=self._value,
            ),
        )
        if res.success:
            print(f"Successfully set {self._attr} to {self._value}.")
            if len(res.reason) > 0:
                print(res.reason)
        else:
            print(f"Unable to set {self._attr} to {self._value}.")
            if len(res.reason) > 0:
                print(res.reason)
        # Add timeout
        self.halt(silent=True)
