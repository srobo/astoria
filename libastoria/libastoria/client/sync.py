from typing import Dict, Generic, List, Optional, Type

from pydantic import parse_obj_as

from libastoria.models import DisksDomain, ProcessDomain, DataT

class DataDomain(Generic[DataT]):

    def __init__(self, name: str, domain_t: Type[DataT]) -> None:
        self._name = name
        self._model = parse_obj_as(domain_t, {})  # TODO: Fetch over HTTP lol

    @property
    def data(self) -> DataT:
        return self._model

    def request(self, name: str, data: Optional[Dict[str, str]] = None) -> None:
        """
        Perform a request.

        :param name: The name of the request.
        :param data: Optionally, any data required by the request.
        :returns: None
        :raises AstoriaRequestException: The request was not successful.
        """
        pass


class AstoriaClient:
    """Client for accessing Astoria."""

    def __init__(self) -> None:
        self.disks = DataDomain[DisksDomain]("disks", DisksDomain)
        self.process = DataDomain[ProcessDomain]("process", ProcessDomain)
