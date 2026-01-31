"""Metadata Manager Application."""

import logging

import click

from .metadata_manager import MetadataManager

LOGGER = logging.getLogger(__name__)


@click.command("astmetad")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: str | None) -> None:
    """Metadata Manager Application Entrypoint."""
    MetadataManager(verbose, config_file).execute()


if __name__ == "__main__":
    main()
