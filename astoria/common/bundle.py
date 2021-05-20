"""Schema, validation and comparison for Kit Bundle files."""
from typing import List

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
    region: str


class CodeBundle(BaseModel):
    """Schema for code bundle information."""

    bundle: BundleInfo
    kit: KitInfo
    wifi: WiFiInfo

    class Config:
        """Pydantic config."""

        extra = "forbid"

    def check_kit_version_is_compatible(self, system_kit_info: KitInfo) -> List[str]:
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
        bundle_match = KIT_VERSION_REGEX.match(self.kit.version)

        bundle_warnings: List[str] = []

        # These are technically unreachable as we are already validating that
        # the version strings match the regex in the schema. Thus these two
        # checks existing mainly for satisfying the type checker and can be
        # safely ignored from test coverage.
        if system_match is None:  # pragma: no cover
            raise RuntimeError("Invalid system kit version")
        if bundle_match is None:  # pragma: no cover
            raise RuntimeError("Invalid bundle kit version")

        if system_match['epoch'] != bundle_match['epoch']:
            raise IncompatibleKitVersionException(
                "Code Bundle was built for a different version of the kit.",
            )

        if system_match['dev']:
            bundle_warnings.append("WARNING: Running on DEVELOPMENT BUILD")

        if system_match['major'] != bundle_match['major'] or \
                system_match['minor'] != bundle_match['minor']:
            bundle_warnings.append(
                "⚠ Your kit software is unsupported and requires an "
                "update. Please update the kit software.",
            )
        elif system_match['patch'] != bundle_match['patch']:
            bundle_warnings.append(
                "⚠ Code Bundle was made for a version of the kit software"
                " which is different than the current version.",
            )
        return bundle_warnings
