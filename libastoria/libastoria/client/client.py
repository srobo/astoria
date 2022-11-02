"""Client for Astoria API."""
from typing import Any, Dict, Generic, NamedTuple, Optional, Type

import requests
from pydantic import parse_obj_as

from libastoria.models import DataT, DisksDomain, ProcessDomain


class DomainArgs(NamedTuple):
    """Arguments."""

    session: requests.Session
    base_url: str = "http://localhost:34421/v1/domains"


class DataDomain(Generic[DataT]):
    """Data held in a specific domain."""

    def __init__(self, name: str, domain_t: Type[DataT], args: DomainArgs) -> None:
        self._session = args.session
        self._base_url = args.base_url
        self._name = name
        self._domain_t = domain_t

    def _http_request(self, method: str, url: str) -> Any:
        """
        Make an HTTP request to the Astoria server.
        """
        resp = self._session.request(
            method,
            f"{self._base_url}{url}",
        )
        resp.raise_for_status()
        return resp.json()

    @property
    def data(self) -> DataT:
        """The data."""
        data = self._http_request("GET", f"/{self._name}")
        return parse_obj_as(self._domain_t, data)

    def request(self, name: str, data: Optional[Dict[str, str]] = None) -> None:
        """
        Perform a request.

        :param name: The name of the request.
        :param data: Optionally, any data required by the request.
        :returns: None
        :raises AstoriaRequestException: The request was not successful.
        """
        self._session.post(f"{self._base_url}/{self._name}/{name}", data=data)


class AstoriaClient:
    """Client for accessing Astoria."""

    def __init__(self) -> None:
        _session = requests.Session()
        _args = DomainArgs(session=_session)
        self.disks = DataDomain[DisksDomain]("disks", DisksDomain, _args)
        self.process = DataDomain[ProcessDomain]("process", ProcessDomain, _args)
