"""Helper class to manage broadcast events."""
import logging
from asyncio import PriorityQueue
from json import JSONDecodeError, loads
from typing import TYPE_CHECKING, Any, Generic, Match, Type, TypeVar

from astoria.common.broadcast_event import BroadcastEvent

if TYPE_CHECKING:
    from .wrapper import MQTTWrapper

LOGGER = logging.getLogger(__name__)

T = TypeVar("T", bound=BroadcastEvent)


class BroadcastHelper(Generic[T]):
    """Helper class to manager broadcast events."""

    def __init__(self, mqtt: 'MQTTWrapper', name: str, schema: Type[T]) -> None:
        self._mqtt = mqtt
        self._name = name
        self._schema = schema

        self._event_queue: PriorityQueue[T] = PriorityQueue()
        self._mqtt.subscribe(f"broadcast/{name}", self._handle_broadcast)

    @classmethod
    def get_helper(cls, mqtt: 'MQTTWrapper', schema: Type[T]) -> 'BroadcastHelper[T]':
        """Get the broadcast helper for a given event."""
        return BroadcastHelper[T](mqtt, schema.name, schema)

    async def _handle_broadcast(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """
        Handle a broadcast event message.

        Inserts the event inserts it into the priority queue.
        """
        try:
            ev = self._schema(**loads(payload))
            LOGGER.debug(
                f"Received {ev.event_name} broadcast event from {ev.sender_name}",
            )
            await self._event_queue.put(ev)
        except JSONDecodeError:
            LOGGER.warning(f"Broadcast event {self._name} contained invalid JSON")

    def send(self, **kwargs: Any) -> None:  # type: ignore
        """Send an event."""
        data = self._schema(
            event_name=self._schema.name,
            sender_name=self._mqtt._client_name,
            **kwargs,
        )
        self._mqtt.publish(
            f"broadcast/{self._schema.name}",
            data,
            auto_prefix_client_name=False,
        )

    async def wait_broadcast(self) -> T:
        """
        Wait for an event on the given broadcast.

        :param broadcast_name: The name of the broadcast to wait for.
        """
        return await self._event_queue.get()
