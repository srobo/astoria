"""Test the metadata schema."""
from pathlib import Path
from unittest.mock import patch

import pytest

from astoria.common.config import AstoriaConfig
from astoria.common.metadata import Metadata, RobotMode

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
        os_name="Student Robotics OS",
        os_pretty_name="Student Robotics OS 2023.0.0",
        os_version="2023.0.0",
        usercode_entrypoint="robot.py",
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
    assert metadata.os_name == "Student Robotics OS"
    assert metadata.os_pretty_name == "Student Robotics OS 2023.0.0"
    assert metadata.os_version == "2023.0.0"
    assert metadata.usercode_entrypoint == "robot.py"
    assert metadata.wifi_ssid == "robot"
    assert metadata.wifi_psk == "bees"
    assert metadata.wifi_region == "GB"

    assert metadata.json() == '{"arena": "B", "zone": 12, "mode": "COMP", "marker_offset": 40, "game_timeout": 120, "wifi_enabled": false, "astoria_version": "0.0.0", "kernel_version": "5.0.0", "arch": "x64", ' + \
        '"python_version": "3", "libc_ver": "2.0", "os_name": "Student Robotics OS", "os_pretty_name": "Student Robotics OS 2023.0.0", "os_version": "2023.0.0", "usercode_entrypoint": "robot.py", "wifi_ssid": "robot", "wifi_psk": "bees", "wifi_region": "GB"}'  # noqa: E501


def test_metadata_fields_default() -> None:
    """Test that the fields on the metadata schema work."""
    metadata = Metadata(
        astoria_version="0.0.0",
        kernel_version="5.0.0",
        arch="x64",
        python_version="3",
        libc_ver="2.0",
        usercode_entrypoint="robot.py",
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
    assert metadata.usercode_entrypoint == "robot.py"
    assert metadata.wifi_ssid is None
    assert metadata.wifi_psk is None


def test_metadata_init() -> None:
    """
    Check that we can initialise some default metadata.

    This is quite hard to test as the values will differ depending on
    the environment that the tests are running in. Here we will rely
    on Pydantic complaining if any values are not as expected.
    """
    with CONFIG_PATH.open("rb") as fh:
        config = AstoriaConfig.load_from_file(fh)
        Metadata.init(config)


def test_get_os_release_info() -> None:
    """Test the get_os_release_info() method is able to extract variables correctly."""
    fixture_path = Path('tests/data/os_version')
    version_info = Metadata.get_os_release_info(fixture_path / 'arch')
    assert version_info.get('NAME') == 'Arch Linux'
    assert version_info.get('PRETTY_NAME') == "Arch Linux"
    assert version_info.get('ID') == 'arch'
    assert version_info.get('BUILD_ID') == 'rolling'
    assert version_info.get('ANSI_COLOR') == "38;2;23;147;209"
    assert version_info.get('HOME_URL') == 'https://archlinux.org/'
    assert version_info.get('DOCUMENTATION_URL') == 'https://wiki.archlinux.org/'
    assert version_info.get('SUPPORT_URL') == 'https://bbs.archlinux.org/'
    assert version_info.get('BUG_REPORT_URL') == 'https://bugs.archlinux.org/'
    assert version_info.get('LOGO') == 'archlinux-logo'
    assert version_info.get('VERSION') is None
    assert version_info.get('VERSION_ID') is None

    version_info = Metadata.get_os_release_info(fixture_path / 'fedora17')
    assert version_info.get('NAME') == 'Fedora'
    assert version_info.get('VERSION') == '17 (Beefy Miracle)'
    assert version_info.get('ID') == 'fedora'
    assert version_info.get('VERSION_ID') == '17'
    assert version_info.get('PRETTY_NAME') == 'Fedora 17 (Beefy Miracle)'
    assert version_info.get('ANSI_COLOR') == '0;34'
    assert version_info.get('CPE_NAME') == 'cpe:/o:fedoraproject:fedora:17'
    assert version_info.get('HOME_URL') == 'https://fedoraproject.org/'
    assert version_info.get('BUG_REPORT_URL') == 'https://bugzilla.redhat.com/'

    version_info = Metadata.get_os_release_info(fixture_path / 'poky')
    assert version_info.get('ID') == 'poky'
    assert version_info.get('NAME') == 'Poky (Yocto Project Reference Distro)'
    assert version_info.get('VERSION') == "4.0.1 (kirkstone)"
    assert version_info.get('VERSION_ID') == '4.0.1'
    assert version_info.get('PRETTY_NAME') == \
           'Poky (Yocto Project Reference Distro) 4.0.1 (kirkstone)'
    assert version_info.get('DISTRO_CODENAME') == 'kirkstone'


@pytest.mark.parametrize(
    "version_data,expected_brand",
    [
        ("8", "Mac OS"),
        ("10.9", "Mac OS X"),
        ("10.11", "Mac OS X"),
        ("10.12", "macOS"),
        ("11.3", "macOS"),
        ("12.5", "macOS"),
    ],
)
def get_macos_release_info(version_data: str, expected_brand: str) -> None:
    """Test that we correctly get the Mac version data."""
    with patch("platform.mac_ver") as mock_mac_ver:
        mock_mac_ver.return_value = (version_data, "", "")
        assert Metadata.get_macos_release_info() == {
            'NAME': expected_brand,
            'PRETTY_NAME': f"{expected_brand} {version_data}",
            'VERSION_ID': version_data,
        }
        mock_mac_ver.assert_called_once()
