"""Wifi Daemon - Handles Hotspot and WiFi Client connection."""
import asyncio
from typing import Optional

import click
import uvloop

from .wifi_manager import WiFiManager


@click.command("astwifid")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:
    """The WiFi Manager Application Entrypoint."""
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        wifid = WiFiManager(verbose, config_file)
        runner.run(wifid.run())


if __name__ == "__main__":
    main()
