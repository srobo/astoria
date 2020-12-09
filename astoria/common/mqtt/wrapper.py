"""MQTT Wrapper."""

from typing import Optional

import gmqtt
from pydantic import BaseModel

from astoria.common.config import MQTTBrokerInfo
from astoria.common.messages.base import ManagerMessage

from .topic import Topic


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
        last_will: Optional[ManagerMessage],
    ) -> None:
        self._client_name = client_name
        self._broker_info = broker_info
        self._last_will = last_will

        self._client = gmqtt.Client(
            self._client_name,
            will_message=self.last_will_message,
        )

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
            raise RuntimeError("Attempting connection, but client is already connected.")
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
            raise RuntimeError(
                "Attempting disconnection, but client is already disconnected.",
            )

        await self._client.disconnect()

        if self.is_connected:
            raise RuntimeError("Disconnection was attempted, but was unsuccessful")

    def publish(
        self,
        topic: str,
        payload: BaseModel,
        *,
        retain: bool = False,
    ) -> None:
        """Publish a payload to the broker."""
        if not self.is_connected:
            raise RuntimeError(
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
