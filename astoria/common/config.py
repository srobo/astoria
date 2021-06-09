"""
Configuration schema for Astoria.

Common to all components.
"""
import re
from pathlib import Path
from typing import IO, Optional

from pydantic import BaseModel, validator
from toml import load


class MQTTBrokerInfo(BaseModel):
    """MQTT Broker Information."""

    host: str
    port: int
    enable_tls: bool = False
    topic_prefix: str = "astoria"
    force_protocol_version_3_1: bool = False

    class Config:
        """Pydantic config."""

        extra = "forbid"


KIT_VERSION_REGEX = re.compile(r"^(?P<epoch>\d+)\.(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<dev>dev)?(?::(?P<hash>[0-9a-f]{5,40})(?:@(?P<branch>\w+))?)?$")  # noqa: E501


class KitInfo(BaseModel):
    """Kit Information."""

    name: str
    version: str

    @validator('version')
    def version_must_match_regex(cls, v: str) -> str:
        """Validate that the version matches the regex."""
        if not KIT_VERSION_REGEX.match(v):
            raise ValueError("version does not match format")
        return v

    class Config:
        """Pydantic config."""

        extra = "forbid"


class WiFiInfo(BaseModel):
    """System settings for WiFi."""

    interface: str
    bridge: str
    enable_wpa3: bool

    class Config:
        """Pydantic config."""

        extra = "forbid"


class SystemInfo(BaseModel):
    """System settings that don't find elsewhere."""

    cache_dir: Path

    class Config:
        """Pydantic config."""

        extra = "forbid"


class AstoriaConfig(BaseModel):
    """Config schema for Astoria."""

    mqtt: MQTTBrokerInfo
    kit: KitInfo
    wifi: WiFiInfo
    system: SystemInfo

    class Config:
        """Pydantic config."""

        extra = "forbid"

    @classmethod
    def _get_config_path(cls, config_str: Optional[str] = None) -> Path:
        """Check for a config file or search the filesystem for one."""
        CONFIG_SEARCH_PATHS = [
            Path("astoria.toml"),
            Path("/etc/astoria.toml"),
        ]
        if config_str is None:
            for path in CONFIG_SEARCH_PATHS:
                if path.exists() and path.is_file():
                    return path
        else:
            path = Path(config_str)
            if path.exists() and path.is_file():
                return path
        raise FileNotFoundError("Unable to find config file.")

    @classmethod
    def load(cls, config_str: Optional[str] = None) -> 'AstoriaConfig':
        """Load the config."""
        config_path = cls._get_config_path(config_str)
        with config_path.open("r") as fh:
            return cls.load_from_file(fh)

    @classmethod
    def load_from_file(cls, fh: IO[str]) -> 'AstoriaConfig':
        """Load the config from a file."""
        return cls(**load(fh))
