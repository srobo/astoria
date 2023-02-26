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
from .lifecycle import AccessPointInfo, WiFiLifecycle

LOGGER = logging.getLogger(__name__)


class WiFiManager(MetadataHandlerMixin, StateManager[WiFiManagerMessage]):
    """
    WiFi Management Daemon.

    Receives metadata information from astmetad and manages the WiFi.
    """

    name = "astwifid"

    dependencies = ["astmetad"]

    def _init(self) -> None:
        self._lifecycle_lock = asyncio.Lock()
        self._lifecycle: Optional[WiFiLifecycle] = None

        self._mqtt.subscribe("astmetad", self.handle_astmetad_message)

    async def main(self) -> None:
        """Main routine for astwifid."""
        # Wait whilst the program is running.
        await self.wait_loop()

        # Stop the hotspot when we shutdown
        async with self._lifecycle_lock:
            if self._lifecycle:
                await self._lifecycle.stop()

    def _is_hardware_available(self) -> bool:
        required_interfaces = [self.config.wifi.interface, self.config.wifi.bridge]
        all_interfaces_available = all(
            Path(f"/sys/class/net/{interface}").exists()
            for interface in required_interfaces
        )
        if not all_interfaces_available:
            LOGGER.warning("Some physical interfaces were not available.")
        return all_interfaces_available

    def _get_lifecycle(self, metadata: Metadata) -> Optional[WiFiLifecycle]:
        hotspot_can_run = all([
            metadata.wifi_enabled,
            metadata.wifi_ssid is not None,
            metadata.wifi_psk is not None,
            metadata.wifi_region is not None,
            self._is_hardware_available(),
        ])
        if hotspot_can_run:
            # The types here are validated by the above if statement.
            ap_info = AccessPointInfo(
                metadata.wifi_ssid,  # type: ignore
                metadata.wifi_psk,  # type: ignore
                metadata.wifi_region,  # type: ignore
            )
            return WiFiHotspotLifeCycle(ap_info, self.config.wifi)
        return None

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

    def _start_lifecycle(self, lifecycle: WiFiLifecycle) -> None:
        """
        Start a new WiFi lifecycle.

        This function assumes that the caller already holds the lifecycle lock.
        """
        self._lifecycle = lifecycle
        self.status = WiFiManagerMessage(
            status=WiFiManagerMessage.Status.RUNNING,
            hotspot_running=True,
        )
        asyncio.ensure_future(self._lifecycle.run())

    async def handle_metadata(self, metadata: Metadata) -> None:
        """
        Update the state of the hotspot based on the current metadata.

        :param metadata: The metadata included in the update.
        """
        LOGGER.debug("Received new metadata.")
        async with self._lifecycle_lock:
            new_lifecycle = self._get_lifecycle(metadata)
            if self._lifecycle:
                LOGGER.debug("A lifecycle already exists.")
                if new_lifecycle:
                    if self._lifecycle == new_lifecycle:
                        LOGGER.debug("WiFi is setup as required, taking no actions.")
                    else:
                        LOGGER.info("WiFi details have changed. Restarting.")

                        LOGGER.debug(f"Stopping existing {self._lifecycle.name}.")
                        await self._lifecycle.stop()

                        LOGGER.debug(f"Starting {new_lifecycle.name}.")
                        self._start_lifecycle(new_lifecycle)
                else:
                    LOGGER.info(f"Stopping existing {self._lifecycle.name}.")
                    await self._lifecycle.stop()
                    self.status = WiFiManagerMessage(
                        status=WiFiManagerMessage.Status.RUNNING,
                        hotspot_running=False,
                    )
                    self._lifecycle = None
            else:
                if new_lifecycle:
                    LOGGER.debug(f"Starting {new_lifecycle.name}.")
                    self._start_lifecycle(new_lifecycle)
                else:
                    LOGGER.debug("No WiFi is required, taking no actions.")
