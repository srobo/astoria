"""State Consumer base class."""
import asyncio
import logging
from abc import ABCMeta

from .data_component import DataComponent

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class StateConsumer(DataComponent, metaclass=ABCMeta):
    """
    State Consumer.

    A process that accesses some state.
    """

    async def _post_connect(self) -> None:
        """Overridable callback after MQTT connection."""
        await self._mqtt.wait_dependencies()
