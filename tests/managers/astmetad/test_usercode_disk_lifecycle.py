"""Tests for the usercode disk lifecycle."""
import shutil
from pathlib import Path
from typing import Callable, Iterator, List, Optional

import pytest

from astoria.astmetad.metadata_disk_lifecycle import UsercodeDiskLifecycle
from astoria.common.config import AstoriaConfig
from astoria.common.disks import DiskInfo, DiskType, DiskUUID

LifecycleFactory = Callable[[Optional[str]], UsercodeDiskLifecycle]


def find_section(iterator: Iterator[str], deliminator: Optional[str]) -> List[str]:
    """
    Split out a section of the error file.

    :param iterable: An iterator of the lines in the file.
    :param deliminator: The section deliminator, or None if EOF is allowed.
    :returns: A list of lines in the section.
    """
    lines: List[str] = []
    for line in iterator:
        if line == deliminator:
            return lines
        lines.append(line)

    # If a deliminator is required but we are at the end of the file,
    # then raise an exception. Otherwise return the lines.
    if deliminator:
        raise RuntimeError("Deliminator not found.")
    return lines


class TestUsercodeDiskLifecycle:
    """Test the usercode disk lifecycle."""

    ERROR_FILENAME = "robot-settings-error.txt"

    @pytest.fixture
    def lifecycle_factory(
        self,
        data_dir: Path,
        tmpdir: Path,
        config: AstoriaConfig,
    ) -> LifecycleFactory:
        """
        A factory method for constructing UsercodeDiskLifecycle objects.

        The fixture uses a tmpdir and copies in the robot-settings.toml file
        that needs to be tested.
        """

        def _inner(config_name: Optional[str]) -> UsercodeDiskLifecycle:
            if config_name:
                config_path = data_dir / f"robot-settings/{config_name}.toml"
                shutil.copy(config_path, tmpdir / "robot-settings.toml")

            uuid = DiskUUID("temp")
            info = DiskInfo(
                uuid=uuid,
                mount_path=tmpdir,
                disk_type=DiskType.USERCODE,
            )
            return UsercodeDiskLifecycle(
                uuid,
                info,
                config,
            )

        return _inner

    def test_load_valid_settings(self, lifecycle_factory: LifecycleFactory) -> None:
        """Test that a valid settings file is loaded."""
        lifecycle = lifecycle_factory("valid")
        assert lifecycle.diff_data == {
            "usercode_entrypoint": "entrypoint.py",
            "wifi_enabled": "True",
            "wifi_psk": "eightcharacters",
            "wifi_region": "GB",
            "wifi_ssid": "robot-ABC",
        }
        assert not lifecycle._disk_info.mount_path.joinpath(
            self.ERROR_FILENAME,
        ).exists()

    def test_no_settings(self, lifecycle_factory: LifecycleFactory) -> None:
        """Test that a new settings file is generated if one does not exist."""
        lifecycle = lifecycle_factory(None)
        assert lifecycle.diff_data.keys() == {
            "usercode_entrypoint",
            "wifi_enabled",
            "wifi_psk",
            "wifi_region",
            "wifi_ssid",
        }
        assert lifecycle.diff_data["usercode_entrypoint"] == "robot.py"
        assert not lifecycle._disk_info.mount_path.joinpath(
            self.ERROR_FILENAME,
        ).exists()

    def test_bad_unicode(self, lifecycle_factory: LifecycleFactory) -> None:
        """Test that we handle bad unicode in the settings file."""
        lifecycle = lifecycle_factory("bad-unicode")
        assert lifecycle.diff_data.keys() == {
            "usercode_entrypoint",
            "wifi_enabled",
            "wifi_psk",
            "wifi_region",
            "wifi_ssid",
        }
        assert lifecycle.diff_data["usercode_entrypoint"] == "robot.py"
        error_file = lifecycle._disk_info.mount_path.joinpath(self.ERROR_FILENAME)
        assert error_file.exists()

        assert error_file.read_text().splitlines() == [
            "There was an error loading your robot-settings.toml",
            "Your robot-settings.toml has been overwritten.",
            "",
            "Unicode Error: 'utf-8' codec can't decode byte 0x93 in position 1: invalid start byte",  # noqa: E501
        ]

    @pytest.mark.parametrize(
        "filename,error",
        [
            (
                "blank",
                [
                    "robot-settings.toml did not match schema: 3 validation errors for ParsingModel[RobotSettings]",  # noqa: E501
                    "__root__ -> team_tla",
                    "  field required (type=value_error.missing)",
                    "__root__ -> usercode_entrypoint",
                    "  field required (type=value_error.missing)",
                    "__root__ -> wifi_psk",
                    "  field required (type=value_error.missing)",
                    "",
                ],
            ),
            ("bad-toml", ["Invalid TOML: Invalid value (at line 5, column 15)", ""]),
            (
                "extra-config",
                [
                    "robot-settings.toml did not match schema: 1 validation error for ParsingModel[RobotSettings]",  # noqa: E501
                    "__root__ -> bees",
                    "  extra fields not permitted (type=value_error.extra)",
                    "",
                ],
            ),
            (
                "invalid-fields",
                [
                    "robot-settings.toml did not match schema: 3 validation errors for ParsingModel[RobotSettings]",  # noqa: E501
                    "__root__ -> team_tla",
                    "  Team name did not match format: ABC, ABC1 etc. (type=value_error)",
                    "__root__ -> usercode_entrypoint",
                    "  Value must only contain ASCII characters. (type=value_error)",
                    "__root__ -> wifi_psk",
                    "  WiFi PSK must be 8 - 63 characters long. (type=value_error)",
                    "",
                ],
            ),
        ],
    )
    def test_error_generated(
        self,
        filename: str,
        error: List[str],
        data_dir: Path,
        lifecycle_factory: LifecycleFactory,
    ) -> None:
        """Test that robot-settings.toml files generate the correct errors."""
        lifecycle = lifecycle_factory(filename)
        assert lifecycle.diff_data.keys() == {
            "usercode_entrypoint",
            "wifi_enabled",
            "wifi_psk",
            "wifi_region",
            "wifi_ssid",
        }
        assert lifecycle.diff_data["usercode_entrypoint"] == "robot.py"

        error_file = lifecycle._disk_info.mount_path.joinpath(self.ERROR_FILENAME)
        assert error_file.exists()

        # We are deliberately using a generator here to consume the lines.
        error_file_lines = iter(error_file.read_text().splitlines())

        assert find_section(error_file_lines, "") == [
            "There was an error loading your robot-settings.toml",
            "Your robot-settings.toml has been overwritten.",
        ]

        assert find_section(error_file_lines, "Invalid settings file:") == error

        # Skip a new line
        assert find_section(error_file_lines, "") == []

        # Check that the old robot-settings was copied to the error.
        config_path = data_dir / f"robot-settings/{filename}.toml"
        assert (
            find_section(
                error_file_lines,
                None,
            )
            == config_path.read_text().splitlines()
        )
