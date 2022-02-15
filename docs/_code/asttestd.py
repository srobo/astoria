"""Test Manager Application."""

import asyncio
import logging
from typing import Optional

import click

from astoria.common.ipc import ManagerMessage
from astoria.common.manager import StateManager

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


@click.command("asttestd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:
    """Test Manager Application Entrypoint."""
    testd = TestManager(verbose, config_file)
    loop.run_until_complete(testd.run())


class TestManager(StateManager[ManagerMessage]):
    """Astoria Test State Manager."""

    name = "asttestd"
    dependencies = ["astdiskd"]

    def _init(self) -> None:
        pass

    @property
    def offline_status(self) -> ManagerMessage:
        """
        Status to publish when the manager goes offline.

        This status should ensure that any other components relying
        on this data go into a safe state.
        """
        return ManagerMessage(
            status=ManagerMessage.Status.STOPPED,
        )

    async def main(self) -> None:
        """Main routine for asttestd."""
        self.status = ManagerMessage(
            status=ManagerMessage.Status.RUNNING,
        )

        # Wait whilst the program is running.
        await self.wait_loop()


if __name__ == "__main__":
    main()
