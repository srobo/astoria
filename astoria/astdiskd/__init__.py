"""Disk Manager Application."""

import asyncio
import logging
from typing import Optional

import click

from .disk_manager import DiskManager

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


@click.command("astdiskd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:
    """Disk Manager Application Entrypoint."""
    diskd = DiskManager(verbose, config_file)
    loop.run_until_complete(diskd.run())


if __name__ == "__main__":
    main()
