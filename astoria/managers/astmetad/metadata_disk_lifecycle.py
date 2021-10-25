"""Lifecycle classes to load metadata from disks."""

import asyncio
import logging
from abc import ABCMeta, abstractmethod
from json import JSONDecodeError, loads
from typing import Dict

from astoria.common.messages.astdiskd import DiskInfo, DiskUUID

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


class UsercodeDiskLifecycle(AbstractMetadataDiskLifecycle):
    """Load and validate metadata from a usercode disk."""

    def extract_diff_data(self) -> Dict[str, str]:
        """
        Extract the diff data from the disk.

        Loads wifi.toml fom the disk.
        """
        return {}
