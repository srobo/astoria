"""
System Configuration schema for Astoria.

Common to all components.
"""
import sys
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional

from pydantic import BaseModel, parse_obj_as

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


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
    initial_log_lines: List[str] = []

    class Config:
        """Pydantic config."""

        extra = "forbid"


class DiskManagerInfo(BaseModel):
    """Settings specifically for astdiskd."""

    ignored_mounts: List[Path] = []


class ProcessManagerInfo(BaseModel):
    """Settings specifically for astprocd."""

    default_usercode_entrypoint: str = "robot.py"


class AstoriaConfig(BaseModel):
    """Config schema for Astoria."""

    mqtt: MQTTBrokerInfo
    wifi: WiFiInfo
    astdiskd: DiskManagerInfo = DiskManagerInfo()  # Optional section
    astprocd: ProcessManagerInfo = ProcessManagerInfo()  # Optional section
    system: SystemInfo
    env: Dict[str, str] = {}

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
        with config_path.open("rb") as fh:
            return cls.load_from_file(fh)

    @classmethod
    def load_from_file(cls, fh: BinaryIO) -> 'AstoriaConfig':
        """Load the config from a file."""
        return parse_obj_as(cls, tomllib.load(fh))
