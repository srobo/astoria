"""Test the WiFi hotspot lifecycle."""

import asyncio
from pathlib import Path
from typing import List, Tuple

import pytest

from astoria.common.config import AstoriaConfig
from astoria.common.messages.astmetad import Metadata
from astoria.consumers.astwifid import WiFiHotspotLifeCycle


class FakeHostapdWiFiHotspotLifeCycle(WiFiHotspotLifeCycle):
    """WiFiHotspotLifeCycle but with a fake hostapd binary."""

    HOSTAPD_BINARY = "tests/data/hostapd/fake_hostapd.sh"


@pytest.fixture
def config() -> None:
    """Load a config file."""
    path = Path("tests/data/config/valid.toml")
    with path.open() as fh:
        return AstoriaConfig.load_from_file(fh)


@pytest.fixture
def lifecycle() -> WiFiHotspotLifeCycle:
    """Get an instance of the WiFiHotspotLifeCycle."""
    return FakeHostapdWiFiHotspotLifeCycle(
        "ssid",
        "pskpskpskpsk",
        "region",
        "interface",
        "bridge",
        True,
    )


@pytest.fixture
def valid_hostapd_config() -> str:
    """Get a valid hostapd config to compare."""
    hostapd_config_path = Path("tests/data/hostapd/config.txt")
    return hostapd_config_path.read_text(encoding="utf-8")


def test_wifi_hotspot_lifecycle_constructor(lifecycle: WiFiHotspotLifeCycle) -> None:
    """Test that we can construct a WiFiHotspotLifeCycle."""
    assert lifecycle._ssid == "ssid"
    assert lifecycle._psk == "pskpskpskpsk"
    assert lifecycle._region == "region"
    assert lifecycle._interface == "interface"
    assert lifecycle._enable_wpa3 is True


def test_wifi_hotspot_hostapd_config_generation(
        lifecycle: WiFiHotspotLifeCycle,
        valid_hostapd_config: str,
) -> None:
    """Test that we generate a hostapd config correctly."""
    assert lifecycle._config_file is None
    lifecycle.generate_hostapd_config()
    assert lifecycle._config_file is not None

    config_path = Path(lifecycle._config_file.name)

    assert config_path.exists()
    assert config_path.is_file()
    assert config_path.read_text(encoding='utf-8') == valid_hostapd_config


@pytest.mark.asyncio
async def test_wifi_hotspot_start_stop(
        lifecycle: WiFiHotspotLifeCycle,
) -> None:
    """Test that we can start and stop the hotspot."""
    assert not lifecycle._running

    for _ in range(3):
        # Start it
        asyncio.ensure_future(lifecycle.run_hotspot())
        await asyncio.sleep(0.02)
        assert lifecycle._proc is not None
        assert lifecycle._config_file is not None  # Should generate the config
        config_file = Path(lifecycle._config_file.name)
        assert lifecycle._running

        # Stop it
        await lifecycle.stop_hotspot()
        assert not lifecycle._running
        assert lifecycle._proc is None
        assert lifecycle._config_file is not None
        assert not config_file.exists()


METADATA_TEST_CASES: List[Tuple[str, str, str, bool]] = [
    ("ssid", "pskpskpskpsk", "region", False),
    ("ssid2", "pskpskpskpsk", "region", True),
    ("ssid", "pskpskpskpskpskpsk", "region", True),
    ("ssid", "pskpskpskpsk", "otherregion", True),
]


@pytest.mark.parametrize("ssid,psk,region,outcome", METADATA_TEST_CASES)
def test_wifi_hotspot_metadata_changed(
        config: AstoriaConfig,
        lifecycle: WiFiHotspotLifeCycle,
        ssid: str,
        psk: str,
        region: str,
        outcome: bool,
) -> None:
    """Test that we can check if metadata changes."""
    metadata = Metadata.init(config)
    metadata.wifi_ssid = ssid
    metadata.wifi_psk = psk
    metadata.wifi_region = region
    assert lifecycle.has_metadata_changed(metadata) == outcome
