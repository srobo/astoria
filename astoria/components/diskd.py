"""Disk Manager Application."""

import logging

import click

from astoria.common.manager import ManagerDaemon

LOGGER = logging.getLogger(__name__)


@click.command("astdiskd")
@click.option("-v", "--verbose", is_flag=True)
def main(*, verbose: bool) -> None:
    """Disk Manager Application Entrypoint."""
    diskd = DiskManager(verbose)

    diskd.run()


class DiskManager(ManagerDaemon):
    """Astoria Disk Manager."""

    name = "astdiskd"

    def _init(self) -> None:
        self._loop = True

    def _run(self) -> None:
        while(self._loop):
            pass

    def _halt(self) -> None:
        self._loop = False

if __name__ == "__main__":
    main()
