"""Schema, validation and comparison for Kit Bundle files."""
from typing import Optional

from pydantic import BaseModel

from .config import KIT_VERSION_REGEX, KitInfo


class IncompatibleKitVersionException(Exception):
    """The kit version was incompatible with the bundle version."""


class BundleInfo(BaseModel):
    """Code Bundle Info Schema."""

    version: str


class WiFiInfo(BaseModel):
    """Code Bundle WiFi Information schema."""

    ssid: str
    psk: str
    enabled: bool
    region: str  # Might want to make this some kind of enum


class CodeBundle(BaseModel):
    """Schema for bundle.toml."""

    bundle: BundleInfo
    kit: KitInfo
    wifi: WiFiInfo

    class Config:
        """Pydantic config."""

        extra = "forbid"

    def check_kit_version_is_compatible(self, system_kit_info: KitInfo) -> Optional[str]:
        """
        Check that the kit version is compatible.

        :returns: Message to show to the user
        :raises IncompatibleKitVersionException:
        """
        if system_kit_info.name != self.kit.name:
            raise IncompatibleKitVersionException(
                f"Code Bundle was for {self.kit.name}, but the kit is "
                f"{system_kit_info.name}. Refusing to start code as software may"
                f" not be compatible.",
            )

        system_match = KIT_VERSION_REGEX.match(system_kit_info.version)
        bundle_match = KIT_VERSION_REGEX.match(system_kit_info.version)

        if system_match is None:
            raise RuntimeError("Invalid system kit version")
        if bundle_match is None:
            raise RuntimeError("Invalid bundle kit version")

        if system_match['epoch'] != bundle_match['epoch']:
            raise IncompatibleKitVersionException(
                "Code Bundle was built for a different version of the kit.",
            )

        if system_match['dev']:
            user_message = "WARNING: Running on DEVELOPMENT BUILD\n"
        else:
            user_message = ""

        if system_match['major'] != bundle_match['major'] or \
                system_match['minor'] != bundle_match['minor']:
            user_message += "⚠ Your kit software is unsupported and requires an " \
                            "update. Please update the kit software."

        if system_match['patch'] != bundle_match['patch']:
            user_message += "⚠ Code Bundle was made for a version of the kit software" \
                            " which is newer than the current version."
        return user_message or None
