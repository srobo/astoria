"""Configuration schemas for Astoria."""

from .system import AstoriaConfig
from .user import SSID_PREFIX, RobotSettings

__all__ = [
    "AstoriaConfig",
    "RobotSettings",
    "SSID_PREFIX",
]
