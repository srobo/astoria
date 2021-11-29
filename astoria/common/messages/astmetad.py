"""Types for astmetad."""
import platform
import random
import re
import secrets
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator

from astoria import __version__
from astoria.common.config import AstoriaConfig

from .base import ManagerMessage

SSID_PREFIX = "robot-"
MAX_SSID_LENGTH = 32  # SSIDs must be no more than 32 octets.


class RobotMode(Enum):
    """Running Status of the manager daemon."""

    COMP = "COMP"
    DEV = "DEV"


class Metadata(BaseModel):
    """Astoria Metadata."""

    class Config:
        """Pydantic config."""

        validate_assignment = True

    @classmethod
    def init(cls, config: AstoriaConfig) -> 'Metadata':
        """
        Initialise the metadata and populate with data.

        Based on information from software and the astoria configuration.
        """
        uname = platform.uname()
        return cls(
            astoria_version=__version__,
            kernel_version=uname.release,
            arch=uname.machine,
            python_version=platform.python_version(),
            libc_ver="".join(platform.libc_ver()),
            usercode_entrypoint=config.astprocd.default_usercode_entrypoint,
        )

    def is_wifi_valid(self) -> bool:
        """
        Check if the WiFi configuration is valid to be turned on.

        Checks that the WiFi is enabled and that the config params are set.Optional
        :return: boolean indicating whether the WiFi can be turned on.
        """
        return all([
            self.wifi_enabled,
            self.wifi_ssid is not None,
            self.wifi_psk is not None,
            self.wifi_region is not None,
        ])

    # From Meta USB
    arena: str = "A"
    zone: int = 0
    mode: RobotMode = RobotMode.DEV
    marker_offset: int = 0
    game_timeout: Optional[int] = None
    wifi_enabled: bool = True

    # From Software
    astoria_version: str
    kernel_version: str
    arch: str
    python_version: str
    libc_ver: str

    # From robot settings file
    usercode_entrypoint: str
    wifi_ssid: Optional[str] = None
    wifi_psk: Optional[str] = None
    wifi_region: Optional[str] = None


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
