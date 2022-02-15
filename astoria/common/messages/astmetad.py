"""Types for astmetad."""
import random
import re
import secrets

from pydantic import BaseModel, validator

from astoria.common.config import AstoriaConfig
from astoria.common.ipc import ManagerMessage
from astoria.common.metadata import Metadata

SSID_PREFIX = "robot-"
MAX_SSID_LENGTH = 32  # SSIDs must be no more than 32 octets.


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


class MetadataManagerMessage(ManagerMessage):
    """
    Status message for Metadata Manager.

    Published to /astoria/astmetad
    """

    metadata: Metadata
