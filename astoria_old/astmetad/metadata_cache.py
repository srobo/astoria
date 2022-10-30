"""Cache metadata attributes on disk."""

import logging
from json import JSONDecodeError, dumps, loads
from pathlib import Path
from typing import Dict, Optional, Set

LOGGER = logging.getLogger(__name__)


class MetadataCache:
    """Manages loading and updating data from the metadata cache."""

    def __init__(
        self,
        cached_keys: Set[str],
        *,
        cache_path: Path = Path("/var/srobo/astmetad-cache.json"),
    ) -> None:
        """
        Construct the metadata cache.

        :param cached_keys: Keys to allow in the cache.
        :param cache_path: Path to the cache file in an appropriate location.
        """
        self._cached_keys = cached_keys
        self._cache_path = cache_path
        self._ensure_cache_exists()
        self._data = self._read_cache()

    def _ensure_cache_exists(self) -> None:
        """
        Check whether the metadata cache exists.

        If the cache does not exist, it will be created with no data.
        """
        LOGGER.info(f"Cache file is {self._cache_path}")
        if not self._cache_path.exists():
            LOGGER.debug("Cache file does not exist!")

            # Ensure parent directory exists
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)

            LOGGER.info("Creating new cache file.")
            self._write_cache({})

    def _read_cache(self) -> Dict[str, str]:
        """
        Read the data from the cache file.

        Ignore any data that isn't permitted.

        :return: Data from the cache file.
        """
        LOGGER.debug("Reading data from cache.")
        with self._cache_path.open("r") as fh:
            raw_data = fh.read()

        try:
            unvalidated_data = loads(raw_data)

            # Validate that everything is a string.
            for k, v in unvalidated_data.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    LOGGER.warning(f"Invalid JSON data in cache: {raw_data}")
                    return {}

            data = {k: v for k, v in unvalidated_data.items() if k in self._cached_keys}

            if data != unvalidated_data:
                LOGGER.warning("Bad keys in cache, re-writing cache!")
                self._write_cache(data)
            return data

        except JSONDecodeError:
            LOGGER.warning(f"Invalid JSON data in cache: {raw_data}")
            return {}

    def _write_cache(self, data: Dict[str, str]) -> None:
        """
        Write the data to the cache file.

        :param data: Data to write to the cache file.
        """
        LOGGER.debug(f"Writing data to cache: {data}")
        with self._cache_path.open("w") as fh:
            fh.write(dumps(data))

    @property
    def data(self) -> Dict[str, str]:
        """The cached data."""
        return self._data

    def update_cached_attr(self, key: str, value: Optional[str]) -> None:
        """
        Update a cached attribute.

        :param key: The key of the attribute to update.
        :param value: The value to give the attribute.

        :raises ValueError: Key is not permitted in cache.
        """
        if key not in self._cached_keys:
            raise ValueError(
                f"Tried to cache {key}, but it is not allowed to be cached.",
            )
        else:
            if key not in self._data or self._data[key] != value:
                if value is None:
                    LOGGER.info(f"Deleting {key} from cache.")
                    self._data.pop(key, None)  # Remove the key from the cache.
                else:
                    LOGGER.info(f"Updated cache: {key} -> {value}")
                    self._data[key] = str(value)  # Make sure the value is a string
                self._write_cache(self._data)
