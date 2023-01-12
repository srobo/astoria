"""
Astoria WiFi Daemon.

Manages a WiFi hotspot for the robot.
"""
import asyncio
import logging
import os
import signal
import tempfile
from typing import IO, Optional

from astoria.common.metadata import Metadata

LOGGER = logging.getLogger(__name__)


class WiFiHotspotLifeCycle:
    """Manages the lifecycle of the hostapd process."""

    HOSTAPD_BINARY: str = "hostapd"

    def __init__(
            self,
            ssid: str,
            psk: str,
            region: str,
            interface: str,
            bridge: str,
            enable_wpa3: bool,
    ) -> None:
        LOGGER.info("Starting WiFi Hotspot lifecycle")
        self._ssid: str = ssid
        self._psk: str = psk
        self._region: str = region
        self._interface: str = interface
        self._bridge: str = bridge
        self._enable_wpa3: bool = enable_wpa3

        self._config_file: Optional[IO[bytes]] = None
        self._proc: Optional[asyncio.subprocess.Process] = None
        self._running: bool = False

    def has_metadata_changed(self, metadata: Metadata) -> bool:
        """Checks if the hotspot's properties match that of a set of metadata."""
        return not all(
            [
                self._ssid == metadata.wifi_ssid,
                self._psk == metadata.wifi_psk,
                self._region == metadata.wifi_region,
            ],
        )

    async def run_hotspot(self) -> None:
        """Starts the hostapd process."""
        self._running = True
        LOGGER.info(f"Starting WiFi Hotspot \"{self._ssid}\" on {self._interface}")
        self.generate_hostapd_config()
        if self._config_file is not None:
            while self._running:
                self._proc = await asyncio.create_subprocess_exec(
                    self.HOSTAPD_BINARY,
                    self._config_file.name,
                )
                LOGGER.info(f"{self.HOSTAPD_BINARY} started wth PID: {self._proc.pid}")
                sc = await self._proc.wait()
                if sc is None:
                    continue
                LOGGER.info(f"{self.HOSTAPD_BINARY} terminated with status code {sc}")

        else:
            raise RuntimeError(  # pragma: nocover
                "Tried to start hotspot, but the config file was not set.",
            )

    def generate_hostapd_config(self) -> None:
        """Generates a configuration file for hostapd based on the current metadata."""
        self._config_file = tempfile.NamedTemporaryFile(delete=False)
        LOGGER.debug(
            f"Writing {self.HOSTAPD_BINARY} configuration to {self._config_file.name}",
        )
        config = {
            "interface": self._interface,
            "bridge": self._bridge,
            "ssid": self._ssid,
            "country_code": self._region,
            "channel": 6,
            "hw_mode": "g",
            # Bit field: bit0 = WPA, bit1 = WPA2
            "wpa": 2,
            # Bit field: 1=wpa, 2=wep, 3=both
            "auth_algs": 1,
            # Set of accepted cipher suites; disabling insecure TKIP
            "wpa_pairwise": "CCMP",
            # Set of accepted key management algorithms
            # SAE = WPA3, WPA-PSK = WPA2
            "wpa_key_mgmt": "WPA-PSK",
            "wpa_passphrase": self._psk,
        }

        if self._enable_wpa3:
            config["wpa_key_mgmt"] = "SAE WPA-PSK"
            # Management frame support (802.11w)
            # Most client devices will not connect to a
            # WPA3-SAE secured AP unless it is using 802.11w.
            # This must be supported by both the AP and client.
            config["ieee80211w"] = 2
            config["sae_require_mfp"] = 1

        contents = "\n".join(f"{k}={v}" for k, v in config.items())

        self._config_file.write(contents.encode())
        self._config_file.close()

    async def stop_hotspot(self) -> None:
        """Stops the hostapd process."""
        self._running = False
        LOGGER.info("Stopping WiFi Hotspot")
        if self._proc is not None:
            self._proc.send_signal(signal.SIGINT)
            try:
                await asyncio.wait_for(self._proc.communicate(), timeout=5.0)
            except asyncio.TimeoutError:
                if self._proc is not None:
                    LOGGER.info(f"Sent SIGKILL to pid {self._proc.pid}")
                    self._proc.send_signal(signal.SIGKILL)
            except AttributeError:
                # Under some circumstances, there is a race condition such that
                # _proc becomes None whilst the communicate timeout is running.
                # We want to catch and discard this error.
                pass
            self._proc = None

        if self._config_file:
            os.unlink(self._config_file.name)
