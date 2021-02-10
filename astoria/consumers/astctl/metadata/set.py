"""Command to set a metadata attribute."""
import asyncio
from typing import Optional

import click

from astoria.common.manager_requests import MetadataSetManagerRequest
from astoria.consumers.astctl.command import Command

loop = asyncio.get_event_loop()


@click.command("set")
@click.argument("attribute")
@click.argument("value")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def set(attribute: str, value: str, *, verbose: bool, config_file: Optional[str]) -> None:
    """Set a metadata attribute."""
    command = SetMetadataCommand(attribute, value, verbose, config_file)
    loop.run_until_complete(command.run())


class SetMetadataCommand(Command):
    """Set a metadata attribute."""

    dependencies = ["astmetad"]

    def __init__(
        self,
        attribute: str,
        value: str,
        verbose: bool,
        config_file: Optional[str],
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
