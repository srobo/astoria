"""Common code for manager daemons."""
import asyncio
import atexit
import logging
from abc import ABCMeta, abstractmethod
from signal import SIGHUP, SIGINT, SIGTERM, Signals, signal
from types import FrameType
from typing import Union

import gmqtt
from pydantic import BaseModel

from astoria import __version__

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class ManagerDaemon(metaclass=ABCMeta):
    """
    A manager daemon.

    Communicates data with a MQTT server.
    """

    def __init__(self, verbose: bool) -> None:
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
        LOGGER.info(f"{self.name} v{__version__} - {self.__doc__}")

        self._running = True

        self._mqtt_client = gmqtt.Client(self.name, will_message=self.last_will_message)
        self._mqtt_stop_event = asyncio.Event()

        atexit.register(lambda: self.halt() if self._running else None)
        signal(SIGHUP, self._signal_halt)
        signal(SIGINT, self._signal_halt)
        signal(SIGTERM, self._signal_halt)

        self._init()

    def _init(self) -> None:
        """Initialisation of the manager."""
        pass

    def run(self) -> None:
        """Run the daemon."""
        LOGGER.info("Ready")
        loop.run_until_complete(self._run_main())

    async def _run_main(self) -> None:
        await self._mqtt_client.connect("mqtt.eclipse.org")
        await self.main()
        await self._mqtt_client.disconnect()

    def halt(self) -> None:
        """
        Halt the daemon.

        Should stop the daemon safely.
        """
        self._running = False  # Prevent atexit calling this twice
        LOGGER.info("Halting")
        self._mqtt_stop_event.set()

    @abstractmethod
    async def main(self) -> None:
        """Main."""
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the daemon."""
        raise NotImplementedError

    @property
    @abstractmethod
    def last_will_message(self) -> gmqtt.Message:
        """The last will message for the MQTT client."""
        raise NotImplementedError

    @property
    @abstractmethod
    def mqtt_prefix(self) -> str:
        """The topic prefix for MQTT."""
        raise NotImplementedError

    def _signal_halt(self, signal: Signals, __: FrameType) -> None:
        LOGGER.debug(f"Received {Signals(signal).name}, triggering halt")
        self.halt()

    async def mqtt_publish(self, topic: str, payload: Union[BaseModel, str]) -> None:
        """Mock publish."""
        if isinstance(payload, BaseModel):
            payload = payload.json()
        self._mqtt_client.publish(
            f"{self.mqtt_prefix}/{topic}",
            payload,
            qos=1,
            retain=True,
        )
