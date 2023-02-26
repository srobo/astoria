"""Wifi Daemon - Handles Hotspot and WiFi Client connection."""
import asyncio
from typing import Optional

import click

from .wifi_manager import WiFiManager

loop = asyncio.get_event_loop()


@click.command("astwifid")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:
    """The WiFi Manager Application Entrypoint."""
    wifid = WiFiManager(verbose, config_file)
    loop.run_until_complete(wifid.run())


if __name__ == "__main__":
    main()
