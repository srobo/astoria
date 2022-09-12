"""Rauc Update Manager Application."""

import asyncio
import logging
from typing import Optional

import click

from .rauc_manager import RaucUpdateManager

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


@click.command("astraucd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:
    """Rauc Update Manager Application Entrypoint."""
    raucd = RaucUpdateManager(verbose, config_file)
    loop.run_until_complete(raucd.run())


if __name__ == "__main__":
    main()
