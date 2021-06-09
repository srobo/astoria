"""
Data Component base class.

A data component represents the common functionality between
State Managers and Consumers. It handles connecting to the broker
and managing the event loop.
"""
import asyncio
import logging
import signal
import sys
from abc import ABCMeta, abstractmethod
from signal import SIGHUP, SIGINT, SIGTERM
from types import FrameType
from typing import List, Optional

from pydantic import BaseModel

from astoria import __version__

from .config import AstoriaConfig
from .mqtt.wrapper import MQTTWrapper

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class DataComponent(metaclass=ABCMeta):
    """
    Data Component base class.

    A data component represents the common functionality between
    State Managers and Consumers. It handles connecting to the broker
    and managing the event loop.
    """

    config: AstoriaConfig

    def __init__(self, verbose: bool, config_file: Optional[str]) -> None:
        self.config = AstoriaConfig.load(config_file)

        self._setup_logging(verbose)
        self._setup_event_loop()
        self._setup_mqtt()

        self._init()

    def _setup_logging(self, verbose: bool, *, welcome_message: bool = True) -> None:
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

        if welcome_message:
            LOGGER.info(f"{self.name} v{__version__} - {self.__doc__}")

    def _setup_event_loop(self) -> None:
        self._stop_event = asyncio.Event()

        loop.add_signal_handler(SIGHUP, self.halt)
        loop.add_signal_handler(SIGINT, self.halt)
        loop.add_signal_handler(SIGTERM, self.halt)

    def _setup_mqtt(self) -> None:
        self._mqtt = MQTTWrapper(
            self.name,
            self.config.mqtt,
            last_will=self.last_will,
            dependencies=self.dependencies,
            no_dependency_event=self._stop_event,
        )

    def _init(self) -> None:
        """
        Initialisation of the data component.

        Called in the constructor of the parent class.
        """
        pass

    def _exit(self, signals: signal.Signals, frame_type: FrameType) -> None:
        sys.exit(0)

    @property
    @abstractmethod
    def name(self) -> str:
        """
        MQTT client name of the data component.

        This should be unique, as clashes will cause unexpected disconnections.
        """
        raise NotImplementedError

    @property
    def dependencies(self) -> List[str]:
        """State Managers to depend on."""
        return []

    @property
    def last_will(self) -> Optional[BaseModel]:
        """Last will and testament of the MQTT client."""
        return None

    async def run(self) -> None:
        """Entrypoint for the data component."""
        await self._pre_connect()
        await self._mqtt.connect()
        await self._post_connect()

        await self.main()

        await self._pre_disconnect()
        await self._mqtt.disconnect()
        await self._post_disconnect()

    async def wait_loop(self) -> None:
        """Wait until the data component is halted."""
        await self._stop_event.wait()

    def halt(self, *, silent: bool = False) -> None:
        """Stop the component."""
        if not silent:
            LOGGER.info("Halting")
        self._stop_event.set()

    @abstractmethod
    async def main(self) -> None:
        """Main method of the data component."""
        raise NotImplementedError

    async def _pre_connect(self) -> None:
        """Overridable callback before MQTT connection."""
        pass

    async def _pre_disconnect(self) -> None:
        """Overridable callback before MQTT disconnection."""
        pass

    async def _post_connect(self) -> None:
        """Overridable callback after MQTT connection."""
        pass

    async def _post_disconnect(self) -> None:
        """Overridable callback after MQTT disconnection."""
        pass
