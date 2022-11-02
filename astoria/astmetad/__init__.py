"""Metadata Manager Application."""

import asyncio
import logging
from typing import Optional

import click

from .metadata_manager import MetadataManager

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


@click.command("astmetad")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:
    """Metadata Manager Application Entrypoint."""
    metad = MetadataManager(verbose, config_file)
    loop.run_until_complete(metad.run())


if __name__ == "__main__":
    main()
