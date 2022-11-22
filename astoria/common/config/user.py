"""User config file schema."""

import random
import re
import secrets
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


from pydantic import BaseModel, ValidationError, parse_obj_as, validator

from astoria.common.config import AstoriaConfig

SSID_PREFIX = "robot-"
MAX_SSID_LENGTH = 32  # SSIDs must be no more than 32 octets.


class RobotSettingsException(Exception):
    """There was an error with the robot settings file."""


class NoValidRobotSettingsException(RobotSettingsException):
    """The robot settings were not valid."""


class NoRobotSettingsException(RobotSettingsException):
    """The robot settings file does not exist."""


class UnreadableRobotSettingsException(RobotSettingsException):
    """
    Unable to read robot settings file.

    It is probably binary or invalid UTF-8.
    """


class RobotSettings(BaseModel):
    """Schema for robot-settings.toml."""

    team_tla: str
    usercode_entrypoint: str
    wifi_psk: str
    wifi_region: str = "GB"  # Assume GB as that is where most competitors are.
    wifi_enabled: bool = True

    class Config:
        """Pydantic config."""

        extra = "forbid"

    @validator("team_tla")
    def validate_team_tla(cls, val: str) -> str:
        """
        Validate the TLA.

        :param val: The received TLA value.
        :returns: The TLA value.
        """
        if val == "beeeeees":
            return "🐝" * 6

        if not re.match(r"^[A-Z]{3}\d*$", val, re.IGNORECASE):
            raise ValueError("Team name did not match format: ABC, ABC1 etc.")

        if len(val.encode()) > MAX_SSID_LENGTH - len(SSID_PREFIX):
            raise ValueError(
                f"SSID {SSID_PREFIX}{val} is longer than "
                f"maximum length: {MAX_SSID_LENGTH} octets.",
            )

        return val.upper()

    @validator("usercode_entrypoint", "wifi_psk")
    def validate_plain_text(cls, val: str) -> str:
        """Validate that the attributes are plaintext."""
        if not val.isprintable():
            raise ValueError("Value must only contain printable characters.")

        if not val.isascii():
            raise ValueError("Value must only contain ASCII characters.")

        return val

    @validator("usercode_entrypoint")
    def validate_usercode_entrypoint(cls, val: str) -> str:
        """
        Validate that the usercode entrypoint is valid.

        :param val: The entrypoint to validate.
        :returns: The validated entrypoint.
        """
        if val in ["", "."]:
            raise ValueError(f"{val!r} is a disallowed filename.")

        if re.search("/<>|:&", val):
            raise ValueError(f"{val!r} contains an invalid character.")

        if val.startswith(".."):
            raise ValueError(f"{val!r} cannot start with ..")

        return val

    @validator("wifi_psk")
    def validate_wifi_psk(cls, val: str) -> str:
        """
        Validate that the WiFi PSK is valid.

        :param val: The PSK to validate.
        :returns: The validated PSK.
        """
        if len(val) not in range(8, 64):
            raise ValueError("WiFi PSK must be 8 - 63 characters long.")

        return val

    @classmethod
    def generate_default_settings(cls, config: AstoriaConfig) -> 'RobotSettings':
        """Generate default sensible settings for the robot."""
        random_tla = f"ZZZ{random.randint(0, 99999)}"

        # Use random characters for the WiFi password as passphrase schemes
        # such as Diceware are very language specific. This can be changed
        # by competitors if they need to.
        #
        # Also separate every 4 characters by a dash for readability
        passphrase = "-".join(secrets.token_hex(2) for _ in range(3))

        return cls(
            team_tla=random_tla,
            usercode_entrypoint=config.astprocd.default_usercode_entrypoint,
            wifi_psk=passphrase,
        )

    @classmethod
    def load_settings_file(cls, path: Path) -> 'RobotSettings':
        """
        Load the robot settings file.

        :param path: The file to load settings from.
        :raises NoValidRobotSettingsException: The robot settings were not valid.
        :raises NoRobotSettingsException: The robot settings file did not exist.
        :raises UnreadableRobotSettingsException: The robot settings file was unreadable.
        :returns: The robot settings in path.
        """
        if not path.exists():
            raise NoRobotSettingsException(f"{path.name} does not exist.")

        try:
            with path.open("rb") as fh:
                data = tomllib.load(fh)
        except tomllib.TOMLDecodeError as e:
            raise NoValidRobotSettingsException(f"Invalid TOML: {e}")
        except UnicodeDecodeError as e:
            raise UnreadableRobotSettingsException(f"Unicode Error: {e}")

        try:
            return parse_obj_as(RobotSettings, data)
        except ValidationError as e:
            raise NoValidRobotSettingsException(
                f"{path.name} did not match schema: {e}",
            )
