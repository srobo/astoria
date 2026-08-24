"""Disk Manager Application."""

import logging

import click

from .disk_manager import DiskManager

LOGGER = logging.getLogger(__name__)


@click.command("astdiskd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: str | None) -> None:
    """Disk Manager Application Entrypoint."""
    DiskManager(verbose, config_file).execute()


if __name__ == "__main__":
    main()
