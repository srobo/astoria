"""State Consumer base class."""
import asyncio
import logging
from abc import ABCMeta, abstractmethod
from uuid import uuid4

from .data_component import DataComponent

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class StateConsumer(DataComponent, metaclass=ABCMeta):
    """
    State Consumer.

    A process that accesses some state.
    """

    @property
    def name(self) -> str:
        """
        MQTT client name of the data component.

        This should be unique, as clashes will cause unexpected disconnections.
        """
        return f"{self.name_prefix}-{uuid4()}"

    @property
    @abstractmethod
    def name_prefix(self) -> str:
        """Prefix for the non-random bit of the client name."""
        raise NotImplementedError

    async def _post_connect(self) -> None:
        """Overridable callback after MQTT connection."""
        await self._mqtt.wait_dependencies()
