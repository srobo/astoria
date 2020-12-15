"""MQTT Wrapper."""

import asyncio
import logging
from json import loads
from typing import Any, Callable, Coroutine, Dict, List, Match, Optional, Set

import gmqtt
from pydantic import BaseModel

from astoria.common.config import MQTTBrokerInfo
from astoria.common.messages.base import ManagerMessage

from .topic import Topic

LOGGER = logging.getLogger(__name__)

Handler = Callable[[Match[str], str], Coroutine[Any, Any, None]]  # type: ignore


class MQTTWrapper:
    """
    MQTT wrapper class.

    Wraps the functionality that we are using for MQTT, with extra
    sanity checks and validation to make sure that things are less
    likely to go wrong.
    """

    _client: gmqtt.Client

    def __init__(
        self,
        client_name: str,
        broker_info: MQTTBrokerInfo,
        *,
        last_will: Optional[BaseModel],
        dependencies: List[str] = [],
        no_dependency_event: Optional[asyncio.Event] = None,
    ) -> None:
        self._client_name = client_name
        self._broker_info = broker_info
        self._last_will = last_will
        self._dependencies = dependencies
        self._no_dependency_event = no_dependency_event

        self._dependency_events: Dict[str, asyncio.Event] = {
            name: asyncio.Event() for name in self._dependencies
        }

        self._topic_handlers: Dict[Topic, Handler] = {}
        self._dependent_topics: Set[Topic] = set()

        self._client = gmqtt.Client(
            self._client_name,
            will_message=self.last_will_message,
        )

        self._client.reconnect_retries = 0

        self._client.on_message = self.on_message
        self._client.on_connect = self.on_connect
        self._client.on_disconnect = self.on_disconnect

        self.subscribe("+", self._dependency_message_handler)

    @property
    def is_connected(self) -> bool:
        """Determine if the client connected to the broker."""
        return self._client.is_connected

    @property
    def last_will_message(self) -> Optional[gmqtt.Message]:
        """Last will and testament message for this client."""
        if self._last_will is not None:
            return gmqtt.Message(
                self.mqtt_prefix,
                self._last_will.json(),
                retain=True,
            )
        else:
            return None

    @property
    def mqtt_prefix(self) -> str:
        """The topic prefix for MQTT."""
        return f"{self._broker_info.topic_prefix}/{self._client_name}"

    async def connect(self) -> None:
        """Connect to the broker."""
        if self.is_connected:
            LOGGER.error("Attempting connection, but client is already connected.")
        mqtt_version = gmqtt.constants.MQTTv50
        if self._broker_info.force_protocol_version_3_1:
            mqtt_version = gmqtt.constants.MQTTv311

        await self._client.connect(
            self._broker_info.host,
            port=self._broker_info.port,
            ssl=self._broker_info.enable_tls,
            version=mqtt_version,
        )

    async def disconnect(self) -> None:
        """Disconnect from the broker."""
        if not self.is_connected:
            LOGGER.error(
                "Attempting disconnection, but client is already disconnected.",
            )

        await self._client.disconnect()

        if self.is_connected:
            raise RuntimeError("Disconnection was attempted, but was unsuccessful")

    def on_connect(
        self,
        client: gmqtt.client.Client,
        flags: int,
        rc: int,
        properties: Dict[str, List[int]],
    ) -> None:
        """Callback for mqtt connection."""
        for topic in self._topic_handlers:
            LOGGER.debug(f"Subscribing to {topic}")
            client.subscribe(str(topic))

    def on_disconnect(self, client: gmqtt.client.Client, packet: bytes) -> None:
        """Callback for mqtt disconnection."""
        LOGGER.debug("MQTT client disconnected")
        if self._no_dependency_event is not None:
            self._no_dependency_event.set()

    async def on_message(
        self,
        client: gmqtt.client.Client,
        topic: str,
        payload: bytes,
        qos: int,
        properties: Dict[str, int],
    ) -> gmqtt.constants.PubRecReasonCode:
        """Callback for mqtt messages."""
        LOGGER.debug(f"Message received on {topic} with payload: {payload!r}")
        for t, handler in self._topic_handlers.items():
            match = t.match(topic)
            if match:
                asyncio.ensure_future(self.wait_dependencies())
                LOGGER.debug(f"Calling {handler.__name__} to handle {topic}")
                asyncio.ensure_future(handler(match, payload.decode()))

        return gmqtt.constants.PubRecReasonCode.SUCCESS

    def publish(
        self,
        topic: str,
        payload: BaseModel,
        *,
        retain: bool = False,
    ) -> None:
        """Publish a payload to the broker."""
        if not self.is_connected:
            LOGGER.error(
                "Attempted to publish message, but client is not connected.",
            )

        if len(topic) == 0:
            topic_complete = Topic.parse(self.mqtt_prefix)
        else:
            topic_complete = Topic.parse(f"{self.mqtt_prefix}/{topic}")
        if not topic_complete.is_publishable:
            raise ValueError(f"Cannot public to MQTT topic: {topic_complete}")
        self._client.publish(
            str(topic_complete),
            payload.json(),
            qos=1,
            retain=retain,
        )

    def subscribe(
        self,
        topic: str,
        callback: Handler,
        *,
        ignore_deps: bool = False,
    ) -> None:
        """
        Subscribe to an MQTT Topic.

        Callback is called when a message arrives.

        Should be called before the MQTT wrapper is connected.
        """
        if len(topic) == 0:
            topic_complete = Topic.parse(self.mqtt_prefix)
        else:
            topic_complete = Topic.parse(f"{self._broker_info.topic_prefix}/{topic}")

        self._topic_handlers[topic_complete] = callback
        if not ignore_deps:
            self._dependent_topics.add(topic_complete)

    async def wait_dependencies(self) -> None:
        """Wait for all dependencies."""
        if len(self._dependencies) > 0:
            LOGGER.debug("Waiting for " + ", ".join(self._dependencies))

            tasks = [asyncio.gather(
                *(event.wait() for event in self._dependency_events.values()),
            )]

            if self._no_dependency_event is not None:
                tasks.append(self._no_dependency_event.wait())  # type: ignore

            await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )

    @property
    def has_dependencies(self) -> bool:
        """Are the dependencies of the manager available?."""
        return all(event.is_set() for event in self._dependency_events.values())

    async def _dependency_message_handler(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """Handle status messages from state managers."""
        manager = match.group(1)
        info = ManagerMessage(**loads(payload))
        LOGGER.debug(f"Status update from {manager}: {info.status}")
        if info.status is ManagerMessage.Status.RUNNING:
            try:
                self._dependency_events[manager].set()
            except KeyError:
                pass
        else:
            if self.has_dependencies and manager in self._dependency_events:
                LOGGER.warning(f"{manager} is unavailable!")
                if self._no_dependency_event is not None:
                    self._no_dependency_event.set()
