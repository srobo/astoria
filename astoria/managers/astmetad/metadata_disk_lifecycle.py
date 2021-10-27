"""Lifecycle classes to load metadata from disks."""

import asyncio
import logging
from abc import ABCMeta, abstractmethod
from json import JSONDecodeError, loads
from pathlib import Path
from typing import Dict

import toml
from pydantic.error_wrappers import ValidationError

from astoria.common.messages.astdiskd import DiskInfo, DiskUUID
from astoria.common.messages.astmetad import SSID_PREFIX, RobotSettings

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class AbstractMetadataDiskLifecycle(metaclass=ABCMeta):
    """Load and validate metadata from a disk."""

    def __init__(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        self._uuid = uuid
        self._disk_info = disk_info

        self._diff = self.extract_diff_data()

    @abstractmethod
    def extract_diff_data(self) -> Dict[str, str]:
        """Extract the diff data from the disk."""
        raise NotImplementedError

    @property
    def diff_data(self) -> Dict[str, str]:
        """The data to be used as override."""
        return self._diff


class MetadataDiskLifecycle(AbstractMetadataDiskLifecycle):
    """Load and validate metadata from a JSON file on the disk."""

    def extract_diff_data(self) -> Dict[str, str]:
        """
        Extract the diff data from the disk.

        Loads astoria.json from the disk and parses it as JSON.
        """
        metadata_file_path = self._disk_info.mount_path / "astoria.json"

        try:
            with metadata_file_path.open("r") as fh:
                return loads(fh.read())  # type: ignore
        except FileNotFoundError:
            LOGGER.warning("Unable to find metadata.json.")
        except JSONDecodeError:
            LOGGER.warning("Invalid JSON in astoria.json")
        return {}


class NoValidRobotSettingsException(Exception):
    """The robot settings were not valid or did not exist."""


class UsercodeDiskLifecycle(AbstractMetadataDiskLifecycle):
    """Load and validate metadata from a usercode disk."""

    def _load_settings_file(self, path: Path) -> RobotSettings:
        """
        Load the robot settings file.

        :param path: The file to load settings from.
        :raises NoValidRobotSettingsException: The robot settings were not valid.
        :returns: The robot settings in path.
        """
        if not path.exists():
            raise NoValidRobotSettingsException("File does not exist.")

        try:
            data = toml.load(path)
        except toml.TomlDecodeError:
            raise NoValidRobotSettingsException("Invalid TOML")

        try:
            return RobotSettings(**data)
        except ValidationError as e:
            raise NoValidRobotSettingsException(
                f"Settings did not match schema: {e}",
            )

    def extract_diff_data(self) -> Dict[str, str]:
        """
        Extract the diff data from the disk.

        Loads robot-settings.toml fom the disk.
        """
        robot_settings_file = self._disk_info.mount_path / "robot-settings.toml"
        try:
            settings = self._load_settings_file(robot_settings_file)
        except NoValidRobotSettingsException:
            settings = RobotSettings.generate_default_settings()

            LOGGER.warning("No valid settings, writing sensible defaults.")
            with robot_settings_file.open("w") as fh:
                toml.dump(settings.dict(), fh)

        return {
            "wifi_ssid": SSID_PREFIX + settings.team_tla,
            "wifi_psk": settings.wifi_psk,
            "wifi_region": settings.wifi_region,
            "wifi_enabled": str(settings.wifi_enabled),
        }
