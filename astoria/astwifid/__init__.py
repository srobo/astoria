"""Wifi Daemon - Handles Hotspot and WiFi Client connection."""

import click

from .wifi_manager import WiFiManager


@click.command("astwifid")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: str | None) -> None:
    """The WiFi Manager Application Entrypoint."""
    WiFiManager(verbose, config_file).execute()


if __name__ == "__main__":
    main()
