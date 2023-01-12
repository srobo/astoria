"""Protocol definition for a WiFi lifecycle."""
from typing import NamedTuple, Protocol


class AccessPointInfo(NamedTuple):
    """The information required for an Access Point."""

    ssid: str
    psk: str
    region: str


class WiFiLifecycle(Protocol):
    """A lifecycle that can be executed by astwifid."""

    def __init__(
        self,
        access_point_info: AccessPointInfo,
        interface: str,
        bridge: str,
        enable_wpa3: bool,
    ) -> None:
        ...

    async def run(self) -> None:
        """
        Run the lifecycle.

        This coroutine will exist for the lifetime of the lifecycle.
        """
        ...

    async def stop(self) -> None:
        """Stop the lifecycle."""
        ...
