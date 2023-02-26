"""Definition for a WiFi lifecycle."""
from abc import ABCMeta, abstractmethod
from typing import NamedTuple

from astoria.common.config.system import WiFiInfo


class AccessPointInfo(NamedTuple):
    """The information required for an Access Point."""

    ssid: str
    psk: str
    region: str


class WiFiLifecycle(metaclass=ABCMeta):
    """A lifecycle that can be executed by astwifid."""

    _access_point_info: AccessPointInfo
    _wifi_info: WiFiInfo

    def __init__(
        self,
        access_point_info: AccessPointInfo,
        wifi_info: WiFiInfo,
    ) -> None:
        self._access_point_info = access_point_info
        self._wifi_info = wifi_info

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the lifecycle."""
        raise NotImplementedError  # pragma: nocover

    @property
    def access_point_info(self) -> AccessPointInfo:
        """The access point info for the lifecycle."""
        return self._access_point_info

    @property
    def wifi_info(self) -> WiFiInfo:
        """The WiFi hardware info for the lifecycle."""
        return self._wifi_info

    @property
    def ssid(self) -> str:
        """The SSID of the network."""
        return self.access_point_info.ssid

    @property
    def interface(self) -> str:
        """The physical interface for the WiFi radio."""
        return self.wifi_info.interface

    def __eq__(self, __o: object) -> bool:
        """
        Determine equality of two lifecycle.

        Lifecycles are equal if they are both the same class and have the same access
        point details. This comparison is used to determine if a lifecycle needs to be
        recreated when the metadata is updated.
        """
        access_point_info = getattr(__o, "access_point_info", None)
        return type(__o) is type(self) and access_point_info == self.access_point_info

    @abstractmethod
    async def run(self) -> None:
        """
        Run the lifecycle.

        This coroutine will exist for the lifetime of the lifecycle.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    async def stop(self) -> None:
        """Stop the lifecycle."""
        raise NotImplementedError  # pragma: nocover
