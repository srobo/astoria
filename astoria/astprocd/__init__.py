"""Process Manager Application."""

import logging

import click

from .process_manager import ProcessManager

LOGGER = logging.getLogger(__name__)


@click.command("astprocd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: str | None) -> None:
    """Process Manager Application Entrypoint."""
    ProcessManager(verbose, config_file).execute()


if __name__ == "__main__":
    main()
