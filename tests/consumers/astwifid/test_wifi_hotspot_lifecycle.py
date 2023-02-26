"""Test the WiFi hotspot lifecycle."""

import asyncio
from pathlib import Path

import pytest

from astoria.astwifid.hotspot_lifecycle import WiFiHotspotLifeCycle
from astoria.astwifid.lifecycle import AccessPointInfo
from astoria.common.config import AstoriaConfig
from astoria.common.config.system import WiFiInfo


class FakeHostapdWiFiHotspotLifeCycle(WiFiHotspotLifeCycle):
    """WiFiHotspotLifeCycle but with a fake hostapd binary."""

    HOSTAPD_BINARY = "tests/data/hostapd/fake_hostapd.sh"


@pytest.fixture
def config() -> AstoriaConfig:
    """Load a config file."""
    path = Path("tests/data/config/valid.toml")
    with path.open("rb") as fh:
        return AstoriaConfig.load_from_file(fh)


@pytest.fixture
def lifecycle() -> WiFiHotspotLifeCycle:
    """Get an instance of the WiFiHotspotLifeCycle."""
    return FakeHostapdWiFiHotspotLifeCycle(
        AccessPointInfo("ssid", "pskpskpskpsk", "region"),
        WiFiInfo(interface="interface", bridge="bridge", enable_wpa3=True),
    )


@pytest.fixture
def valid_hostapd_config() -> str:
    """Get a valid hostapd config to compare."""
    hostapd_config_path = Path("tests/data/hostapd/config.txt")
    return hostapd_config_path.read_text(encoding="utf-8")


def test_wifi_hotspot_lifecycle_constructor(lifecycle: WiFiHotspotLifeCycle) -> None:
    """Test that we can construct a WiFiHotspotLifeCycle."""
    assert lifecycle.access_point_info.ssid == "ssid"
    assert lifecycle.access_point_info.psk == "pskpskpskpsk"
    assert lifecycle.access_point_info.region == "region"
    assert lifecycle.wifi_info.interface == "interface"
    assert lifecycle.wifi_info.enable_wpa3 is True


def test_wifi_hotspot_hostapd_config_generation(
        lifecycle: WiFiHotspotLifeCycle,
        valid_hostapd_config: str,
) -> None:
    """Test that we generate a hostapd config correctly."""
    assert lifecycle._config_file is None
    lifecycle._generate_hostapd_config()
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
        asyncio.ensure_future(lifecycle.run())
        await asyncio.sleep(0.02)
        assert lifecycle._proc is not None
        assert lifecycle._config_file is not None  # Should generate the config
        config_file = Path(lifecycle._config_file.name)
        assert lifecycle._running

        # Stop it
        await lifecycle.stop()
        assert not lifecycle._running
        assert lifecycle._proc is None
        assert lifecycle._config_file is not None
        assert not config_file.exists()
