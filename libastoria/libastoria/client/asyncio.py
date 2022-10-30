from typing import AsyncGenerator, Dict, Generic, Optional, Type

from pydantic import parse_obj_as

from libastoria.models import DisksDomain, LogMessage, ProcessDomain, DataT


class StreamDomain(Generic[DataT]):

    def __init__(self, name: str, domain_t: Type[DataT]) -> None:
        self._name = name
        self._model = parse_obj_as(domain_t, {})  # TODO: Fetch over HTTP lol

    async def iter(self) -> AsyncGenerator[DataT, None]:
        yield self._model


class AsyncAstoriaClient:
    """Async Client for accessing Astoria."""

    def __init__(self) -> None:
        self.logs = StreamDomain[LogMessage]("logs", LogMessage)
