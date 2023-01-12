"""
Astoria WiFi Daemon.

Manages a WiFi hotspot for the robot.
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional

from astoria.common.components import StateManager
from astoria.common.ipc import WiFiManagerMessage
from astoria.common.metadata import Metadata
from astoria.common.mixins import MetadataHandlerMixin

from .hotspot_lifecycle import WiFiHotspotLifeCycle

LOGGER = logging.getLogger(__name__)


class WiFiManager(MetadataHandlerMixin, StateManager[WiFiManagerMessage]):
    """
    WiFi Management Daemon.

    Receives metadata information from astmetad and manages the WiFi.
    """

    name = "astwifid"

    dependencies = ["astmetad"]

    def _init(self) -> None:
        self._hotspot_lifecycle: Optional[WiFiHotspotLifeCycle] = None

        self._mqtt.subscribe("astmetad", self.handle_astmetad_message)

    async def main(self) -> None:
        """Main routine for astwifid."""
        # Wait whilst the program is running.
        await self.wait_loop()

        # Stop the hotspot when we shutdown
        if self._hotspot_lifecycle:
            await self._hotspot_lifecycle.stop_hotspot()

    @property
    def offline_status(self) -> WiFiManagerMessage:
        """
        Status to publish when the manager goes offline.

        This status should ensure that any other components relying
        on this data go into a safe state.
        """
        return WiFiManagerMessage(
            status=WiFiManagerMessage.Status.STOPPED,
            hotspot_running=False,
        )

    async def handle_metadata(self, metadata: Metadata) -> None:
        """
        Update the state of the hotspot based on the current metadata.

        :param metadata: The metadata included in the update.
        """
        wifi_interface = Path(f"/sys/class/net/{self.config.wifi.interface}")
        if self._hotspot_lifecycle:
            if metadata.is_wifi_valid() and wifi_interface.exists():
                if self._hotspot_lifecycle.has_metadata_changed(metadata):
                    await self._hotspot_lifecycle.stop_hotspot()
                    self._hotspot_lifecycle = WiFiHotspotLifeCycle(
                        # The types here are checked by is_wifi_valid
                        metadata.wifi_ssid,  # type: ignore
                        metadata.wifi_psk,  # type: ignore
                        metadata.wifi_region,  # type: ignore
                        self.config.wifi.interface,
                        self.config.wifi.bridge,
                        self.config.wifi.enable_wpa3,
                    )
                    self.status = WiFiManagerMessage(
                        status=WiFiManagerMessage.Status.RUNNING,
                        hotspot_running=True,
                    )
                    asyncio.ensure_future(self._hotspot_lifecycle.run_hotspot())
            else:
                # Turn it off!
                await self._hotspot_lifecycle.stop_hotspot()
                self.status = WiFiManagerMessage(
                    status=WiFiManagerMessage.Status.RUNNING,
                    hotspot_running=False,
                )
                self._hotspot_lifecycle = None
        else:
            if metadata.is_wifi_valid() and wifi_interface.exists():
                # Turn it on!
                self._hotspot_lifecycle = WiFiHotspotLifeCycle(
                    # The types here are checked by is_wifi_valid
                    metadata.wifi_ssid,  # type: ignore
                    metadata.wifi_psk,  # type: ignore
                    metadata.wifi_region,  # type: ignore
                    self.config.wifi.interface,
                    self.config.wifi.bridge,
                    self.config.wifi.enable_wpa3,
                )
                self.status = WiFiManagerMessage(
                    status=WiFiManagerMessage.Status.RUNNING,
                    hotspot_running=True,
                )
                asyncio.ensure_future(self._hotspot_lifecycle.run_hotspot())
