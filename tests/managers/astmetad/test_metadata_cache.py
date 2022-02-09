"""Test metadata cache."""

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

import pytest

from astoria.managers.astmetad.metadata_cache import MetadataCache


@pytest.fixture
def empty_temp_dir() -> Generator[Path, None, None]:
    """Use a temporary directory for tests."""
    with TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_metadata_cache_is_created_no_file(empty_temp_dir: Path) -> None:
    """Test that the cache is created if it does not exist."""
    cache_path = empty_temp_dir / "meta" / "meta.json"
    assert not cache_path.exists()
    meta = MetadataCache({"bees"}, cache_path=cache_path)
    assert cache_path.exists()

    # Check data is initially empty
    assert meta.data == {}


def test_metadata_cache_is_read_on_start(empty_temp_dir: Path) -> None:
    """Test that the cache file is loaded on startup."""
    cache_path = empty_temp_dir / "meta.json"

    cache_path.write_text("{\"bees\": \"hive\"}")

    meta = MetadataCache({"bees"}, cache_path=cache_path)

    # Check data is correct
    assert meta.data == {"bees": "hive"}


def test_metadata_cache_is_updated(empty_temp_dir: Path) -> None:
    """Test that the cache file is updated."""
    cache_path = empty_temp_dir / "meta.json"
    meta = MetadataCache({"bees"}, cache_path=cache_path)

    for val in ("hive", "hive", "queen", "honey"):
        meta.update_cached_attr("bees", val)
        assert meta.data == {"bees": val}
        assert cache_path.read_text() == f"{{\"bees\": \"{val}\"}}"


def test_metadata_cache_fails_on_uncacheable_key(empty_temp_dir: Path) -> None:
    """Test that an exception is raised when an uncacheable value is cached."""
    cache_path = empty_temp_dir / "meta.json"
    meta = MetadataCache({"bees"}, cache_path=cache_path)

    with pytest.raises(ValueError):
        meta.update_cached_attr("notbees", "nothive")


def test_metadata_cache_bad_json_is_ignored(empty_temp_dir: Path) -> None:
    """Test that bad json is ignored when loading the cache."""
    cache_path = empty_temp_dir / "meta.json"

    cache_path.write_text("{}{}{{*784u23ijknmmkfeiosafnotjson}}}")

    meta = MetadataCache({"bees"}, cache_path=cache_path)

    # Check data is empty
    assert meta.data == {}

    # Check we can still write to the file.
    meta.update_cached_attr("bees", "hive")
    assert meta.data == {"bees": "hive"}
    assert cache_path.read_text() == "{\"bees\": \"hive\"}"


def test_metadata_cache_non_string_is_ignored(empty_temp_dir: Path) -> None:
    """Test that bad json is ignored when loading the cache."""
    cache_path = empty_temp_dir / "meta.json"

    cache_path.write_text("{\"bees\": \"hive\", \"wasps\": 100}")

    meta = MetadataCache({"bees", "wasps"}, cache_path=cache_path)

    # Check data is empty
    assert meta.data == {}

    # Check we can still write to the file.
    meta.update_cached_attr("bees", "hive")
    assert meta.data == {"bees": "hive"}
    assert cache_path.read_text() == "{\"bees\": \"hive\"}"


def test_metadata_cache_bad_keys_is_ignored(empty_temp_dir: Path) -> None:
    """Test that we ignore the cache if it has bad keys in it."""
    cache_path = empty_temp_dir / "meta.json"

    cache_path.write_text("{\"bees\": \"hive\", \"notbees\": \"not\"}")

    meta = MetadataCache({"bees"}, cache_path=cache_path)

    # Check data and cache are cleaned
    assert meta.data == {"bees": "hive"}
    assert cache_path.read_text() == "{\"bees\": \"hive\"}"

    # Check we can still write to the file.
    meta.update_cached_attr("bees", "bighive")
    assert meta.data == {"bees": "bighive"}
    assert cache_path.read_text() == "{\"bees\": \"bighive\"}"


def test_metadata_cache_remove_key_when_none(empty_temp_dir: Path) -> None:
    """Test that we remove an entry from the cache when the value is None."""
    cache_path = empty_temp_dir / "meta.json"

    cache_path.write_text("{\"bees\": \"hive\"}")

    meta = MetadataCache({"bees"}, cache_path=cache_path)

    meta.update_cached_attr("bees", None)
    assert meta.data == {}
    assert cache_path.read_text() == "{}"
