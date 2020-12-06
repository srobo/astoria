"""MQTT Subscription Registry."""

import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Match,
    Optional,
    Set,
)

import gmqtt

from .topic import Topic

if TYPE_CHECKING:
    from astoria.common.manager import StateManager

Handler = Callable[[Any, Match[str], str], Coroutine[Any, Any, None]]

LOGGER = logging.getLogger(__name__)


class Registry:
    """Subscription Registry."""

    def __init__(self) -> None:
        self._topic_handlers: Dict[Topic, Handler] = {}
        self._dependent_topics: Set[Topic] = set()
        self._manager: Optional['StateManager'] = None

    @property
    def manager(self) -> Optional['StateManager']:
        """Get the current manager."""
        return self._manager

    @manager.setter
    def manager(self, manager: 'StateManager') -> None:
        """Set the current manager."""
        if self._manager is None:
            self._manager = manager

            # Set MQTT callbacks
            self._manager._mqtt_client.on_message = self.on_message
            self._manager._mqtt_client.on_connect = self.on_connect
        else:
            raise ValueError("The Manager can only be set once.")

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
                mngr = self.manager
                if mngr is not None:
                    if t in self._dependent_topics and not mngr.has_dependencies:
                        LOGGER.debug(f"Ignoring message on {topic} due to missing manager deps")
                    else:
                        LOGGER.debug(f"Calling {handler.__name__} to handle {topic}")
                        await handler(mngr, match, payload.decode())
                    break
                else:
                    raise ValueError(
                        "The registry cannot handle a message without \
                        the corresponding manager",
                    )

        return gmqtt.constants.PubRecReasonCode.SUCCESS

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

    def add_handler(
        self,
        topic: str,
        handler: Handler,
        *,
        ignore_deps: bool = False,
    ) -> None:
        """Add a handler."""
        parsed_topic = Topic.parse(topic)
        self._topic_handlers[parsed_topic] = handler
        if not ignore_deps:
            self._dependent_topics.add(parsed_topic)

    def handler(
        self,
        topic: str,
        *,
        ignore_deps: bool = False,
    ) -> Callable[[Handler], Handler]:
        """Register a topic handler."""

        def decorator(f: Handler) -> Handler:
            self.add_handler(topic, f, ignore_deps=ignore_deps)
            return f

        return decorator
