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


class NoValidRobotSettingsException(Exception):
    """The robot settings were not valid or did not exist."""


class RobotSettings(BaseModel):
    """Schema for robot-settings.toml."""

    team_tla: str
    usercode_entrypoint: str
    wifi_psk: str
    wifi_region: str = "GB"  # Assume GB as that is where most competitors are.
    wifi_enabled: bool = True

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
            raise ValueError("Team name did not match format.")

        if len(val) > MAX_SSID_LENGTH - len(SSID_PREFIX):
            raise ValueError(
                f"SSID {SSID_PREFIX}{val} is longer than "
                f"maximum length: {MAX_SSID_LENGTH} octets.",
            )

        return val.upper()

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
        :returns: The robot settings in path.
        """
        if not path.exists():
            raise NoValidRobotSettingsException("File does not exist.")

        try:
            with path.open("rb") as fh:
                data = tomllib.load(fh)
        except tomllib.TOMLDecodeError:
            raise NoValidRobotSettingsException("Invalid TOML")

        try:
            return parse_obj_as(RobotSettings, data)
        except ValidationError as e:
            raise NoValidRobotSettingsException(
                f"Settings did not match schema: {e}",
            )
