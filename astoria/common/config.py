"""
Configuration schema for Astoria.

Common to all components.
"""
from typing import IO

from pydantic import BaseModel
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


KIT_VERSION_REGEX = r"^(\d+)\.(\d+)\.(\d+)\.(\d+)(dev)?(?::([0-9a-f]{5,40})(?:@(\w+))?)?$"


class KitInfo(BaseModel):
    """Kit Information."""

    name: str
    version: str

    class Config:
        """Pydantic config."""

        extra = "forbid"


class AstoriaConfig(BaseModel):
    """Config schema for Astoria."""

    mqtt: MQTTBrokerInfo
    kit: KitInfo

    class Config:
        """Pydantic config."""

        extra = "forbid"

    @classmethod
    def load_from_file(cls, fh: IO[str]) -> 'AstoriaConfig':
        """Load the config from a file."""
        return cls(**load(fh))
