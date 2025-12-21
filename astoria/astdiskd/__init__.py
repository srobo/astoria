"""Disk Manager Application."""

import asyncio
import logging
from typing import Optional

import click
import uvloop

from .disk_manager import DiskManager

LOGGER = logging.getLogger(__name__)


@click.command("astdiskd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:
    """Disk Manager Application Entrypoint."""
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        diskd = DiskManager(verbose, config_file)
        runner.run(diskd.run())


if __name__ == "__main__":
    main()
