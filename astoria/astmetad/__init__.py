"""Metadata Manager Application."""

import asyncio
import logging

import click
import uvloop

from .metadata_manager import MetadataManager

LOGGER = logging.getLogger(__name__)


@click.command("astmetad")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: str | None) -> None:
    """Metadata Manager Application Entrypoint."""
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        metad = MetadataManager(verbose, config_file)
        runner.run(metad.run())


if __name__ == "__main__":
    main()
