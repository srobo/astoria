"""Helper class to manage broadcast events."""
import logging
from asyncio import PriorityQueue
from json import JSONDecodeError, loads
from typing import TYPE_CHECKING, Dict, Match

from astoria.common.broadcast_event import EVENTS, BroadcastEvent

if TYPE_CHECKING:
    from .wrapper import MQTTWrapper

LOGGER = logging.getLogger(__name__)


class BroadcastHelper:
    """Helper class to manager broadcast events."""

    def __init__(self, mqtt: 'MQTTWrapper') -> None:
        self._mqtt = mqtt
        self._event_queues: Dict[str, PriorityQueue[BroadcastEvent]] = {
            name: PriorityQueue() for name in EVENTS.keys()
        }

        self._mqtt.subscribe("broadcast/+", self._handle_broadcast)

    async def _handle_broadcast(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """
        Handle a broadcast event message.

        Checks if the broadcast event is known and inserts it into the
        priority queue for that event.
        """
        broadcast_name = match.group(1)
        if broadcast_name in EVENTS:
            try:
                ev = EVENTS[broadcast_name](**loads(payload))
                LOGGER.debug(
                    f"Received {ev.event_name} broadcast event from {ev.sender_name}",
                )
                await self._event_queues[broadcast_name].put(ev)
            except JSONDecodeError:
                LOGGER.warning(f"Broadcast event {broadcast_name} contained invalid JSON")
        else:
            LOGGER.warning(f"Received unknown broadcast event: {broadcast_name}")
