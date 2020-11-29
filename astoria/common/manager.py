"""Common code for state managers."""
import asyncio
import atexit
import logging
from abc import ABCMeta, abstractmethod
from signal import SIGHUP, SIGINT, SIGTERM, Signals, signal
from types import FrameType
from typing import IO, Union

import gmqtt
from pydantic import BaseModel

from astoria import __version__
from astoria.common.messages.base import ManagerStatusMessage

from .config import AstoriaConfig
from .mqtt import Registry

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class StateManager(metaclass=ABCMeta):
    """
    State Manager.

    A process that stores and mutates some state.
    """

    def __init__(self, verbose: bool, config_file: IO[str], registry: Registry) -> None:
        self.config = AstoriaConfig.load_from_file(config_file)
        self.registry = registry
        self._status = ManagerStatusMessage.ManagerStatus.STOPPED

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

        self._mqtt_client = gmqtt.Client(self.name, will_message=self.last_will_message)
        self._mqtt_stop_event = asyncio.Event()

        self.registry.manager = self

        atexit.register(self.halt)
        signal(SIGHUP, self._signal_halt)
        signal(SIGINT, self._signal_halt)
        signal(SIGTERM, self._signal_halt)

        self._init()

    def _init(self) -> None:
        """Initialisation of the manager."""
        pass

    async def run(self) -> None:
        """Entrypoint for the State Manager."""
        LOGGER.info("Ready")

        mqtt_version = gmqtt.constants.MQTTv50
        if self.config.mqtt.force_protocol_version_3_1:
            mqtt_version = gmqtt.constants.MQTTv311

        await self._mqtt_client.connect(
            self.config.mqtt.host,
            port=self.config.mqtt.port,
            ssl=self.config.mqtt.enable_tls,
            version=mqtt_version,
        )
        await self.set_status(ManagerStatusMessage.ManagerStatus.RUNNING)
        await self.main()
        await self.set_status(ManagerStatusMessage.ManagerStatus.STOPPED)
        await self._mqtt_client.disconnect()

    async def wait_loop(self) -> None:
        """Wait until the state manager is halted."""
        await self._mqtt_stop_event.wait()

    async def set_status(self, status: ManagerStatusMessage.ManagerStatus) -> None:
        """Set the manager status."""
        if status is not self._status:  # Deduplicate messages.
            self._status = status
            await self.mqtt_publish(
                f"status",
                ManagerStatusMessage(status=status),
            )

    def halt(self) -> None:
        """Stop the state manager."""
        self._mqtt_stop_event.set()

    @abstractmethod
    async def main(self) -> None:
        """
        Main method of the state manager.

        Must make a call to ``self.wait_loop()`` to wait for the stop event.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the daemon."""
        raise NotImplementedError

    @property
    def last_will_message(self) -> gmqtt.Message:
        """The MQTT last will and testament."""
        return gmqtt.Message(
            f"{self.mqtt_prefix}/status",
            ManagerStatusMessage(
                status=ManagerStatusMessage.ManagerStatus.STOPPED,
            ).json(),
            retain=True,
        )

    @property
    def mqtt_prefix(self) -> str:
        """The topic prefix for MQTT."""
        return f"{self.config.mqtt.topic_prefix}/{self.name}"

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
