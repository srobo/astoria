"""Lifecycle classes to load metadata from disks."""

import asyncio
import logging
from abc import ABCMeta, abstractmethod
from json import JSONDecodeError, loads
from pathlib import Path
from typing import Dict, Optional

import tomli_w

from astoria.common.config import (
    SSID_PREFIX,
    AstoriaConfig,
    NoRobotSettingsException,
    NoValidRobotSettingsException,
    RobotSettings,
    UnreadableRobotSettingsException,
)
from astoria.common.disks import DiskInfo, DiskUUID

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class AbstractMetadataDiskLifecycle(metaclass=ABCMeta):
    """Load and validate metadata from a disk."""

    def __init__(
        self,
        uuid: DiskUUID,
        disk_info: DiskInfo,
        config: AstoriaConfig,
    ) -> None:
        self._uuid = uuid
        self._disk_info = disk_info
        self._config = config

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


class UsercodeDiskLifecycle(AbstractMetadataDiskLifecycle):
    """Load and validate metadata from a usercode disk."""

    def _write_error_file(
        self,
        file: Path,
        error: str,
        config: Optional[bytes] = None,
    ) -> None:
        """
        Write an error file to the disk.

        :param file: The file to write the error to.
        :param error: An error message.
        :param config: Optionally, a config file to print at the bottom.
        """
        with file.open("wb") as fh:
            fh.writelines([
                b"There was an error loading your robot-settings.toml\n"
                b"Your robot-settings.toml has been overwritten.\n",
                b"\n",
            ])
            fh.write(error.encode())

            if config is not None:
                fh.write(b"\n\n")
                fh.write(b"Invalid settings file:\n\n")
                fh.write(config)

    def _regenerate_config(self, robot_settings_file: Path) -> RobotSettings:
        """Generate a new user settings file and write it to the path."""
        settings = RobotSettings.generate_default_settings(self._config)
        with robot_settings_file.open("wb") as fh:
            tomli_w.dump(settings.dict(), fh)
        return settings

    def _load_settings(self) -> RobotSettings:
        """
        Load the settings from the disk.

        If there is an issue with the settings file, generate a new one
        and write an error message if appropriate.

        :returns: A RobotSettings struct.
        """
        disk_path = self._disk_info.mount_path
        robot_settings_file = disk_path / "robot-settings.toml"
        robot_settings_error_file = disk_path / "robot-settings-error.txt"
        try:
            return RobotSettings.load_settings_file(robot_settings_file)
        except NoRobotSettingsException:
            LOGGER.warning("Settings file not present, writing sensible defaults.")
        except NoValidRobotSettingsException as e:
            LOGGER.warning("No valid settings, writing sensible defaults.")
            LOGGER.warning(str(e))
            self._write_error_file(
                robot_settings_error_file,
                str(e),
                robot_settings_file.read_bytes(),
            )
        except UnreadableRobotSettingsException as e:
            LOGGER.warning("Settings were unreadable, writing sensible defaults.")
            LOGGER.warning(str(e))
            self._write_error_file(robot_settings_error_file, str(e))

        return self._regenerate_config(robot_settings_file)

    def extract_diff_data(self) -> Dict[str, str]:
        """
        Extract the diff data from the disk.

        Loads robot-settings.toml fom the disk.
        """
        settings = self._load_settings()
        return {
            "usercode_entrypoint": settings.usercode_entrypoint,
            "wifi_ssid": SSID_PREFIX + settings.team_tla,
            "wifi_psk": settings.wifi_psk,
            "wifi_region": settings.wifi_region,
            "wifi_enabled": str(settings.wifi_enabled),
        }
