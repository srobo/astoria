"""
Astoria WiFi Daemon.

Manages a WiFi hotspot for the robot.
"""
import asyncio
import logging
import subprocess
from subprocess import check_output, Popen
from json import loads, JSONDecodeError
from pathlib import Path
from typing import Match, Optional

import click
from pydantic import ValidationError

from astoria.common.consumer import StateConsumer
from astoria.common.messages.astmetad import Metadata, MetadataManagerMessage

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


@click.command("astwifid")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def main(*, verbose: bool, config_file: Optional[str]) -> None:
    """WiFi Daemon Application Entrypoint."""
    wifid = WiFiHotspotDaemon(verbose, config_file)
    loop.run_until_complete(wifid.run())


class WiFiHotspotDaemon(StateConsumer):
    name = "astwifid"

    dependencies = ["astmetad"]

    def _init(self) -> None:
        self._lifecycle: Optional[WiFiHotspotLifeCycle] = None

        self._mqtt.subscribe("astmetad", self.handle_astmetad_message)

    async def main(self) -> None:
        """Main routine for astwifid."""
        # Wait whilst the program is running.
        await self.wait_loop()

        # Stop the hotspot when we shutdown
        if self._lifecycle:
            await self._lifecycle.stop_hotspot()

    @property
    def name_prefix(self) -> str:
        return "astwifid"

    async def handle_astmetad_message(
            self,
            match: Match[str],
            payload: str,
    ) -> None:
        if payload:
            try:
                metadata_manager_message = MetadataManagerMessage(**loads(payload))
                await self.handle_metadata(metadata_manager_message.metadata)
            except ValidationError:
                LOGGER.warning("Received bad metadata manager message.")
            except JSONDecodeError:
                LOGGER.warning("Received bad JSON in metadata manager message.")
        else:
            LOGGER.warning("Received empty metadata manager message.")

    async def handle_metadata(self, metadata: Metadata) -> None:

        if self._lifecycle:
            if metadata.wifi_enabled:
                # Check if creds match
                pass
            else:
                # Turn it off!
                await self._lifecycle.stop_hotspot()
                self._lifecycle = None
        else:
            if metadata.wifi_enabled:
                # Turn it on!
                self._lifecycle = WiFiHotspotLifeCycle(
                    metadata.wifi_ssid,
                    metadata.wifi_psk,
                    metadata.wifi_region,
                    metadata.wifi_interface,
                )
                asyncio.ensure_future(self._lifecycle.run_hotspot())


class WiFiHotspotLifeCycle:
    ssid: str
    psk: str
    region: str
    interface: str
    config_file_path: Path = Path("/tmp/astwifid_hostapd_config")
    proc: Optional[Popen] = None
    running = True

    def __init__(self, ssid: str, psk: str, region: str, interface: str) -> None:
        print("Starting WiFi Hotspot lifecycle")
        self.ssid = ssid
        self.psk = psk
        self.region = region
        self.interface = interface

    async def run_hotspot(self) -> None:
        self.running = True
        LOGGER.info(f"Starting WiFi Hotspot \"{self.ssid}\" on {self.interface}")
        self.gen_hostapd_config()
        self.proc = Popen(["hostapd", self.config_file_path])

        while self.running:
            sc = self.proc.poll()
            if sc is None:
                continue

            LOGGER.info(f"hostapd terminated with status code {sc}, restarting...")
            self.proc = Popen(["hostapd", self.config_file_path])
            LOGGER.info(f"hostapd started wth PID: {self.proc.pid}")


    def gen_hostapd_config(self):
        self.config_file_path = Path(check_output(["mktemp"]).decode().strip())
        LOGGER.debug(f"Writing hostapd configuration to {self.config_file_path}")
        config = {
            "interface": self.interface,
            # "bridge": "br0",
            "ssid": self.ssid,
            # "driver": "nl80211",
            "country_code": self.region,
            "channel": 7,
            "hw_mode": "g",
            # Bit field: bit0 = WPA, bit1 = WPA2
            "wpa": 2,
            # Bit field: 1=wpa, 2=wep, 3=both
            "auth_algs": 1,
            # Set of accepted cipher suites; disabling insecure TKIP
            "wpa_pairwise": "CCMP",
            # Set of accepted key management algorithms
            "wpa_key_mgmt": "WPA-PSK",
            "wpa_passphrase": self.psk,
        }
        contents = "\n".join([f"{k}={config.get(k)}" for k in config])

        self.config_file_path.write_text(contents)

    def cleanup_config_file(self):
        self.config_file_path.unlink(missing_ok=True)

    async def stop_hotspot(self) -> None:
        self.running = False
        LOGGER.info("Stopping WiFi Hotspot")
        if self.proc is not None:
            self.proc.send_signal(2)  # SIGINT - equivalent of ^C
        self.cleanup_config_file()


if __name__ == "__main__":
    main()
