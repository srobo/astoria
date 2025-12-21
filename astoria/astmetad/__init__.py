"""Metadata Manager Application."""

import asyncio
import logging
from typing import Optional

import click

from .metadata_manager import MetadataManager

LOGGER = logging.getLogger(__name__)

@click.command("astmetad")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:
    """Metadata Manager Application Entrypoint."""
    metad = MetadataManager(verbose, config_file)
    asyncio.run(metad.run())


if __name__ == "__main__":
    main()
