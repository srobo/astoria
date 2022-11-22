"""Test the user config."""

from pathlib import Path
from typing import Dict, Type, Union

import pytest
from pydantic import ValidationError, parse_obj_as

from astoria.common.config import (
    NoRobotSettingsException,
    NoValidRobotSettingsException,
    RobotSettings,
    UnreadableRobotSettingsException,
)


class TestLoadUserConfig:
    """Test that we can load the user config."""

    @pytest.mark.parametrize(
        "filename",
        ["missing_optional.toml", "valid.toml"],
    )
    def test_load_config(self, filename: Path, data_dir: Path) -> None:
        """Test that we can load valid config files."""
        RobotSettings.load_settings_file(data_dir / "robot-settings" / filename)

    @pytest.mark.parametrize(
        "filename,exception",
        [
            ("bad-toml.toml", NoValidRobotSettingsException),
            ("bad-unicode.toml", UnreadableRobotSettingsException),
            ("blank.toml", NoValidRobotSettingsException),
            ("extra-config.toml", NoValidRobotSettingsException),
            ("invalid-fields.toml", NoValidRobotSettingsException),
            ("non-existent.toml", NoRobotSettingsException),
        ],
    )
    def test_load_config_raises_correct_exception(
        self,
        filename: Path,
        exception: Type[Exception],
        data_dir: Path,
    ) -> None:
        """Test for bad type validation."""
        with pytest.raises(exception):
            RobotSettings.load_settings_file(data_dir / "robot-settings" / filename)


class TestUserSettingsValidation:
    """Test that we validate the user settings properly."""

    @pytest.fixture
    def valid_config(self) -> Dict[str, str]:
        """A dictionary for a valid robot settings."""
        return {
            "team_tla": "ABC",
            "usercode_entrypoint": "robot.py",
            "wifi_psk": "eightcharacters",
            "wifi_region": "GB",
            "wifi_enabled": "true",
        }

    def test_valid_config(self, valid_config: Dict[str, str]) -> None:
        """Test that we can load a valid config."""
        parse_obj_as(RobotSettings, valid_config)

    def test_spurious_config(self, valid_config: Dict[str, str]) -> None:
        """Test that an error is thrown when a spurious field is present."""
        valid_config["bees"] = "yes"
        with pytest.raises(ValidationError) as e:
            parse_obj_as(RobotSettings, valid_config)
        errors = e.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("__root__", "bees")
        assert errors[0]["msg"] == "extra fields not permitted"

    @pytest.mark.parametrize("field", ["team_tla", "usercode_entrypoint", "wifi_psk"])
    def test_error_when_required_field_missing(
        self,
        field: str,
        valid_config: Dict[str, str],
    ) -> None:
        """Test that an error is raised when a required field is missing."""
        del valid_config[field]
        with pytest.raises(ValidationError) as e:
            parse_obj_as(RobotSettings, valid_config)
        errors = e.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("__root__", field)
        assert errors[0]["msg"] == "field required"

    @pytest.mark.parametrize(
        "field,default_val",
        [
            ("wifi_region", "GB"),
            ("wifi_enabled", True),
        ],
    )
    def test_no_error_when_optional_field_missing(
        self,
        field: str,
        default_val: Union[str, bool],
        valid_config: Dict[str, str],
    ) -> None:
        """Test that we allow optional fields to be missing."""
        del valid_config[field]
        config = parse_obj_as(RobotSettings, valid_config)
        assert getattr(config, field) is default_val

    @pytest.mark.parametrize(
        "tla,expected_tla",
        [
            ("ABC", "ABC"),
            ("abc", "ABC"),
            ("abc1", "ABC1"),
            ("aBc126", "ABC126"),
            pytest.param(
                "ABC64723643260767843747824",
                "ABC64723643260767843747824",
                id="32-octets-with-prefix",
            ),
            pytest.param("beeeeees", "🐝🐝🐝🐝🐝🐝", id="bees"),
        ],
    )
    def test_valid_tlas_are_accepted(
        self,
        tla: str,
        expected_tla: str,
        valid_config: Dict[str, str],
    ) -> None:
        """Test that valid team TLAs are accepted."""
        valid_config["team_tla"] = tla
        config = parse_obj_as(RobotSettings, valid_config)
        assert config.team_tla == expected_tla

    @pytest.mark.parametrize(
        "tla,expected_error",
        [
            ("", "Team name did not match format: ABC, ABC1 etc."),
            ("a", "Team name did not match format: ABC, ABC1 etc."),
            ("aaaa", "Team name did not match format: ABC, ABC1 etc."),
            ("123", "Team name did not match format: ABC, ABC1 etc."),
            ("ABC12A", "Team name did not match format: ABC, ABC1 etc."),
            ("1ABC12", "Team name did not match format: ABC, ABC1 etc."),
            ("?!W£", "Team name did not match format: ABC, ABC1 etc."),
            ("bees", "Team name did not match format: ABC, ABC1 etc."),
            pytest.param(
                "ABC647236432607678437478244",
                "SSID robot-ABC647236432607678437478244 is longer than "
                "maximum length: 32 octets.",
                id="33-octets-with-prefix",
            ),
        ],
    )
    def test_invalid_tlas_are_rejected(
        self,
        tla: str,
        expected_error: str,
        valid_config: Dict[str, str],
    ) -> None:
        """Test that an invalid TLA is rejected."""
        valid_config["team_tla"] = tla
        with pytest.raises(ValidationError) as e:
            parse_obj_as(RobotSettings, valid_config)
        errors = e.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("__root__", "team_tla")
        assert errors[0]["msg"] == expected_error

    @pytest.mark.parametrize("psk", ["helloworld", "????????432!{}"])
    def test_valid_psk_are_accepted(
        self,
        psk: str,
        valid_config: Dict[str, str],
    ) -> None:
        """Test that we accept valid wifi PSKs."""
        valid_config["wifi_psk"] = psk
        config = parse_obj_as(RobotSettings, valid_config)
        assert config.wifi_psk == psk

    @pytest.mark.parametrize(
        "psk,expected_error",
        [
            ("", "WiFi PSK must be 8 - 63 characters long."),
            ("short", "WiFi PSK must be 8 - 63 characters long."),
            pytest.param(
                "more-than-63-chars-long-abcdefghijklmnopqrstuvwxyz1234567890!@$%",
                "WiFi PSK must be 8 - 63 characters long.",
                id="64-octets",
            ),
            pytest.param(
                "££££££££",
                "Value must only contain ASCII characters.",
                id="non-ascii",
            ),
            pytest.param(
                "\n",
                "Value must only contain printable characters.",
                id="line-break",
            ),
        ],
    )
    def test_invalid_psks_are_rejected(
        self,
        psk: str,
        expected_error: str,
        valid_config: Dict[str, str],
    ) -> None:
        """Test that an invalid WiFi PSK is rejected."""
        valid_config["wifi_psk"] = psk
        with pytest.raises(ValidationError) as e:
            parse_obj_as(RobotSettings, valid_config)
        errors = e.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("__root__", "wifi_psk")
        assert errors[0]["msg"] == expected_error

    @pytest.mark.parametrize(
        "entrypoint",
        [
            "helloworld",
            "????????432!{}",
            "robot.py",
            ".robot.py",
        ],
    )
    def test_valid_usercode_entrypoint_are_accepted(
        self,
        entrypoint: str,
        valid_config: Dict[str, str],
    ) -> None:
        """Test that we accept valid usercode entrypoints.."""
        valid_config["usercode_entrypoint"] = entrypoint
        config = parse_obj_as(RobotSettings, valid_config)
        assert config.usercode_entrypoint == entrypoint

    @pytest.mark.parametrize(
        "entrypoint,expected_error",
        [
            ("", "'' is a disallowed filename."),
            (".", "'.' is a disallowed filename."),
            ("..", "'..' cannot start with .."),
            ("../bees.py", "'../bees.py' cannot start with .."),
            ("£.py", "Value must only contain ASCII characters."),
            pytest.param(
                "\n",
                "Value must only contain printable characters.",
                id="line-break",
            ),
        ],
    )
    def test_invalid_usercode_entrypoints_are_rejected(
        self,
        entrypoint: str,
        expected_error: str,
        valid_config: Dict[str, str],
    ) -> None:
        """Test that an invalid usercode entrypoint is rejected."""
        valid_config["usercode_entrypoint"] = entrypoint
        with pytest.raises(ValidationError) as e:
            parse_obj_as(RobotSettings, valid_config)
        errors = e.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("__root__", "usercode_entrypoint")
        assert errors[0]["msg"] == expected_error
