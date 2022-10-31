"""Asynchronous client for Astoria."""
from typing import AsyncGenerator, Generic, Type

from pydantic import parse_obj_as

from libastoria.models import DataT, LogMessage


class StreamDomain(Generic[DataT]):
    """A stream."""

    def __init__(self, name: str, domain_t: Type[DataT]) -> None:
        self._name = name
        self._model = parse_obj_as(domain_t, {})

    async def iter(self) -> AsyncGenerator[DataT, None]:
        """Iterate over messages in the stream."""
        yield self._model


class AsyncAstoriaClient:
    """Async Client for accessing Astoria."""

    def __init__(self) -> None:
        self.logs = StreamDomain[LogMessage]("logs", LogMessage)
