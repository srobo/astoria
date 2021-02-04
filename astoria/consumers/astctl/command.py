"""Command base for astctl."""
import asyncio

from astoria.common.consumer import StateConsumer

loop = asyncio.get_event_loop()


class Command(StateConsumer):
    """
    Command base class for astctl.

    Disables the welcome message from the logger.
    """

    name_prefix = "astctl"

    def _setup_logging(self, verbose: bool, *, welcome_message: bool = True) -> None:
        super()._setup_logging(verbose, welcome_message=False)
