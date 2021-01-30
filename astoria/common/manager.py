"""State Manager base class."""
import asyncio
import logging
from abc import ABCMeta, abstractmethod
from json import JSONDecodeError, loads
from typing import Callable, Coroutine, Generic, Match, Type, TypeVar

from .data_component import DataComponent
from .manager_requests import ManagerRequest, RequestResponse
from .messages.base import ManagerMessage

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()

T = TypeVar("T", bound=ManagerMessage)
RequestT = TypeVar("RequestT", bound=ManagerRequest)


class StateManager(DataComponent, Generic[T], metaclass=ABCMeta):
    """
    State Manager.

    A process that stores and mutates some state.
    """

    _status: T

    @property
    def status(self) -> T:
        """Get the status of the state manager."""
        return self._status

    @status.setter
    def status(self, status: T) -> None:
        """Set the status of the state manager."""
        self._status = status
        self._mqtt.publish("", status, retain=True)

    @property
    @abstractmethod
    def offline_status(self) -> T:
        """
        Status to publish when the manager goes offline.

        This status should ensure that any other components relying
        on this data go into a safe state.
        """
        raise NotImplementedError

    @property
    def last_will(self) -> T:
        """Last will and testament of the MQTT client."""
        return self.offline_status

    async def _post_connect(self) -> None:
        """Overridable callback after MQTT connection."""
        LOGGER.info("Ready.")
        await self._mqtt.wait_dependencies()

    async def _pre_disconnect(self) -> None:
        """Change status to offline before disconnecting from the broker."""
        self.status = self.offline_status

    def _register_request(
        self,
        name: str,
        typ: Type[RequestT],
        handler: Callable[[RequestT], Coroutine[None, None, RequestResponse]],
    ) -> None:
        LOGGER.debug(f"Registering {name} request for {self.name} component")

        async def _handler(match: Match[str], payload: str) -> None:
            try:
                req = typ(**loads(payload))
                response = await handler(req)
                self._mqtt.publish(
                    f"request/{name}/{req.uuid}",
                    response,
                )
            except JSONDecodeError:
                LOGGER.warning(f"Received {name} request, but unable to decode JSON")

        self._mqtt.subscribe(f"{self.name}/request/{name}", _handler)
