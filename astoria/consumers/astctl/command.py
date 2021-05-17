"""Command base for astctl."""
import asyncio
from abc import abstractmethod
from json import JSONDecodeError, loads
from typing import Generic, Match, Type, TypeVar
from uuid import uuid4

from astoria.common.consumer import StateConsumer
from astoria.common.messages.base import ManagerMessage

T = TypeVar("T", bound=ManagerMessage)

loop = asyncio.get_event_loop()


class Command(StateConsumer):
    """
    Command base class for astctl.

    Disables the welcome message from the logger.
    """

    @property
    def name(self) -> str:
        """
        MQTT client name of the data component.

        This should be unique, as clashes will cause unexpected disconnections.
        """
        return f"astctl-{uuid4()}"

    def _setup_logging(self, verbose: bool, *, welcome_message: bool = True) -> None:
        super()._setup_logging(verbose, welcome_message=False)


class SingleManagerMessageCommand(Command, Generic[T]):
    """
    A command that waits for the message from a single manager and does something with it.

    Useful for getting data and displaying it.
    """

    @property
    @abstractmethod
    def manager(self) -> str:
        """The manager to receive a message from."""
        raise NotImplementedError

    @property
    @abstractmethod
    def message_schema(self) -> Type[T]:
        """The schema of the message for the manager."""
        raise NotImplementedError

    @abstractmethod
    def handle_message(
        self,
        message: T,
    ) -> None:
        """Do something with the message."""
        raise NotImplementedError

    def _init(self) -> None:
        """Initialise consumer."""
        self._received = False
        self._mqtt.subscribe(self.manager, self._handle_raw_message)

    async def main(self) -> None:
        """Main method of the command."""
        await self.wait_loop()

    async def _handle_raw_message(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """Handle astdiskd status messages."""
        if not self._received:
            self._received = True
            try:
                message = self.message_schema(**loads(payload))
                if message.status == self.message_schema.Status.RUNNING:
                    self.handle_message(message)
                else:
                    print(f"{self.manager} is not running")
            except JSONDecodeError:
                print("Could not decode JSON data.")
        self.halt(silent=True)
