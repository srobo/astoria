"""Common code for state managers."""
import asyncio
import logging
from abc import ABCMeta, abstractmethod
from signal import SIGHUP, SIGINT, SIGTERM
from typing import IO, Generic, List, TypeVar

from astoria import __version__

from .config import AstoriaConfig
from .messages.base import ManagerMessage
from .mqtt.wrapper import MQTTWrapper

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()

T = TypeVar("T", bound=ManagerMessage)


class StateManager(Generic[T], metaclass=ABCMeta):
    """
    State Manager.

    A process that stores and mutates some state.
    """

    _status: T

    def __init__(self, verbose: bool, config_file: IO[str]) -> None:
        self.config = AstoriaConfig.load_from_file(config_file)

        if verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format=f"%(asctime)s {self.name} %(name)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format=f"%(asctime)s {self.name} %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            # Suppress INFO messages from gmqtt
            logging.getLogger("gmqtt").setLevel(logging.WARNING)

        LOGGER.info(f"{self.name} v{__version__} - {self.__doc__}")

        self._mqtt = MQTTWrapper(
            self.name,
            self.config.mqtt,
            last_will=self.offline_status,
        )

        self._stop_event = asyncio.Event()

        loop.add_signal_handler(SIGHUP, self.halt)
        loop.add_signal_handler(SIGINT, self.halt)
        loop.add_signal_handler(SIGTERM, self.halt)

        self._init()

    def _init(self) -> None:
        """Initialisation of the manager."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the daemon."""
        raise NotImplementedError

    @property
    def status(self) -> T:
        """Get the status of the state manager."""
        return self._status

    @status.setter
    def status(self, status: T) -> None:
        """Set the status of the state manager."""
        self._status = status
        self._mqtt.publish("", status, retain=True)

    @property
    @abstractmethod
    def offline_status(self) -> T:
        """
        Status to publish when the manager goes offline.

        This status should ensure that any other components relying
        on this data go into a safe state.
        """
        raise NotImplementedError

    @property
    def dependencies(self) -> List[str]:
        """State Managers to depend on."""
        return []

    async def run(self) -> None:
        """Entrypoint for the State Manager."""
        LOGGER.info("Ready")
        await self._mqtt.connect()

        await self.main()

        self.status = self.offline_status
        await self._mqtt.disconnect()

    async def wait_loop(self) -> None:
        """Wait until the state manager is halted."""
        await self._stop_event.wait()

    def halt(self) -> None:
        """Stop the state manager."""
        LOGGER.info("Halting")
        self._stop_event.set()

    @abstractmethod
    async def main(self) -> None:
        """
        Main method of the state manager.

        Must make a call to ``self.wait_loop()`` to wait for the stop event.
        """
        raise NotImplementedError
