"""Metadata Manager Application."""

import asyncio
import logging
from pathlib import Path
from typing import IO

import click

from astoria.common.manager import StateManager
from astoria.common.messages.astmetad import Metadata, MetadataManagerMessage

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


@click.command("astmetad")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.File('r'), default=Path("astoria.toml"))
def main(*, verbose: bool, config_file: IO[str]) -> None:
    """Metadata Manager Application Entrypoint."""
    metad = MetadataManager(verbose, config_file)
    loop.run_until_complete(metad.run())


class MetadataManager(StateManager[MetadataManagerMessage]):
    """Astoria Metadata State Manager."""

    name = "astmetad"
    dependencies = ["astdiskd"]

    def _init(self) -> None:
        pass

    @property
    def offline_status(self) -> MetadataManagerMessage:
        """
        Status to publish when the manager goes offline.

        This status should ensure that any other components relying
        on this data go into a safe state.
        """
        return MetadataManagerMessage(
            status=MetadataManagerMessage.Status.STOPPED,
            metadata=Metadata.init(self.config),
        )

    async def main(self) -> None:
        """Main routine for astmetad."""
        self.status = MetadataManagerMessage(
            status=MetadataManagerMessage.Status.RUNNING,
            metadata=Metadata.init(self.config),
        )

        # Wait whilst the program is running.
        await self.wait_loop()


if __name__ == "__main__":
    main()
