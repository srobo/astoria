"""Tests for astmetad message definitions."""
from pathlib import Path

from astoria.common.config import AstoriaConfig
from astoria.common.messages.astmetad import (
    Metadata,
    MetadataManagerMessage,
    RobotMode,
)

CONFIG_PATH = Path("tests/data/config/valid.toml")


def test_robot_mode_enum() -> None:
    """Test that RobotMode has the right values and length."""
    assert RobotMode.COMP.value == "COMP"
    assert RobotMode.DEV.value == "DEV"
    assert len(RobotMode) == 2


def test_metadata_fields() -> None:
    """Test that the fields on the metadata schema work."""
    metadata = Metadata(
        arena="B",
        zone=12,
        mode=RobotMode.COMP,
        marker_offset=40,
        game_timeout=120,
        wifi_enabled=False,
        astoria_version="0.0.0",
        kernel_version="5.0.0",
        arch="x64",
        python_version="3",
        libc_ver="2.0",
        kit_name="Unit Testing",
        kit_version="0.0.0",
        wifi_ssid="robot",
        wifi_psk="bees",
        wifi_region="GB",
    )

    assert metadata.arena == "B"
    assert metadata.zone == 12
    assert metadata.mode == RobotMode.COMP
    assert metadata.marker_offset == 40
    assert metadata.game_timeout == 120
    assert metadata.wifi_enabled is False
    assert metadata.astoria_version == "0.0.0"
    assert metadata.kernel_version == "5.0.0"
    assert metadata.arch == "x64"
    assert metadata.python_version == "3"
    assert metadata.libc_ver == "2.0"
    assert metadata.kit_name == "Unit Testing"
    assert metadata.kit_version == "0.0.0"
    assert metadata.wifi_ssid == "robot"
    assert metadata.wifi_psk == "bees"
    assert metadata.wifi_region == "GB"

    assert metadata.json() == '{"arena": "B", "zone": 12, "mode": "COMP", "marker_offset": 40, "game_timeout": 120, "wifi_enabled": false, "astoria_version": "0.0.0", "kernel_version": "5.0.0", "arch": "x64", ' + \
        '"python_version": "3", "libc_ver": "2.0", "kit_name": "Unit Testing", "kit_version": "0.0.0", "wifi_ssid": "robot", "wifi_psk": "bees", "wifi_region": "GB"}'  # noqa: E501


def test_metadata_fields_default() -> None:
    """Test that the fields on the metadata schema work."""
    metadata = Metadata(
        astoria_version="0.0.0",
        kernel_version="5.0.0",
        arch="x64",
        python_version="3",
        libc_ver="2.0",
        kit_name="Unit Testing",
        kit_version="0.0.0",
    )

    assert metadata.arena == "A"
    assert metadata.zone == 0
    assert metadata.mode == RobotMode.DEV
    assert metadata.game_timeout is None
    assert metadata.wifi_enabled is True
    assert metadata.astoria_version == "0.0.0"
    assert metadata.kernel_version == "5.0.0"
    assert metadata.arch == "x64"
    assert metadata.python_version == "3"
    assert metadata.libc_ver == "2.0"
    assert metadata.kit_name == "Unit Testing"
    assert metadata.kit_version == "0.0.0"
    assert metadata.wifi_ssid is None
    assert metadata.wifi_psk is None


def test_metadata_init() -> None:
    """
    Check that we can initialise some default metadata.

    This is quite hard to test as the values will differ depending on
    the environment that the tests are running in. Here we will rely
    on Pydantic complaining if any values are not as expected.
    """
    with CONFIG_PATH.open("r") as fh:
        config = AstoriaConfig.load_from_file(fh)
        Metadata.init(config)


def test_metadata_manager_message_fields() -> None:
    """Test that the metadata manager message has the expected fields."""
    metadata = Metadata(
        astoria_version="0.0.0",
        kernel_version="5.0.0",
        arch="x64",
        python_version="3",
        libc_ver="2.0",
        kit_name="Unit Testing",
        kit_version="0.0.0",
    )

    mmm = MetadataManagerMessage(
        metadata=metadata,
        status=MetadataManagerMessage.Status.RUNNING,
    )

    assert mmm.metadata == metadata
