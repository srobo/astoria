"""Process Manager Application."""

import asyncio
import logging
from typing import Optional

import click

from .process_manager import ProcessManager

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


@click.command("astprocd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:
    """Process Manager Application Entrypoint."""
    testd = ProcessManager(verbose, config_file)
    loop.run_until_complete(testd.run())


if __name__ == "__main__":
    main()
