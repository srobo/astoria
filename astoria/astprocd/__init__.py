"""Process Manager Application."""

import asyncio
import logging
import uvloop
from typing import Optional

import click

from .process_manager import ProcessManager

LOGGER = logging.getLogger(__name__)


@click.command("astprocd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:
    """Process Manager Application Entrypoint."""
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        procd = ProcessManager(verbose, config_file)
        runner.run(procd.run())


if __name__ == "__main__":
    main()
