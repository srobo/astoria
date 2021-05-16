"""Test bundle information functionality."""
from pathlib import Path

import pytest
import toml
from pydantic import ValidationError

from astoria.common.bundle import CodeBundle, IncompatibleKitVersionException
from astoria.common.config import KIT_VERSION_REGEX, KitInfo

DATA_PATH = Path("tests/data/bundle")


def load_bundle(fn: str) -> None:
    """Load a config file."""
    path = DATA_PATH / fn
    with path.open("r") as fh:
        data = toml.load(fh)
        return CodeBundle(**data)


def test_bundle_loads_valid_file() -> None:
    """Test that we can load a valid bundle information file."""
    load_bundle("valid.toml")


def test_bundle_fails_to_load_invalid_toml() -> None:
    """Test that we can't load an invalid toml file."""
    with pytest.raises(toml.TomlDecodeError):
        load_bundle("not.toml")


def test_bundle_fails_to_load_extraneous_fields() -> None:
    """Test that we can't load a bundle with extra fields."""
    with pytest.raises(ValidationError):
        load_bundle("extraneous_fields.toml")


def test_bundle_fails_to_load_missing_fields() -> None:
    """Test that we can't load a bundle with missing fields."""
    with pytest.raises(ValidationError):
        load_bundle("missing_fields.toml")


VALID_VERSION_STRINGS = [
    "0.0.0.0dev",
    "2021.1.0.0",
    "2021.1.0.2:534912@master",
    "2021.1.0.2:534912",
    "2021.1.0.0dev",
    "2021.1.0.2dev:53491266d26fcb504eb4b1d9108de04899832c83",
    "2021.1.0.2dev:53491266d26fcb504eb4b1d9108de04899832c83@master",
]


@pytest.mark.parametrize("version", VALID_VERSION_STRINGS)
def test_valid_version_string_is_accepted(version) -> None:
    """Test that valid version strings are accepted."""
    assert KIT_VERSION_REGEX.match(version) is not None


INVALID_VERSION_STRINGS = [
    "bees",
    "123456789",
    "1.1.1",
    "1.1.1.1.1",
]


@pytest.mark.parametrize("version", INVALID_VERSION_STRINGS)
def test_valid_version_string_is_not_accepted(version) -> None:
    """Test that invalid version strings are not accepted."""
    assert KIT_VERSION_REGEX.match(version) is None


VALID_SYSTEM_BUNDLE_VERSION_PAIRS = [
    ("2021.0.0.0", "2021.0.0.0"),
]


@pytest.mark.parametrize("system,bundle", VALID_SYSTEM_BUNDLE_VERSION_PAIRS)
def test_valid_versions_are_accepted(system, bundle) -> None:
    """Test that valid versions are accepted."""
    system_info = KitInfo(name="Astoria Development", version=system)
    bundle_info = load_bundle("valid.toml")
    bundle_info.kit.version = bundle

    assert len(bundle_info.check_kit_version_is_compatible(system_info)) == 0


INCOMPATIBLE_SYSTEM_BUNDLE_VERSION_PAIRS = [
    ("2020.0.0.0", "2021.0.0.0"),
    ("2022.0.0.0", "2021.0.0.0"),
]


@pytest.mark.parametrize("system,bundle", INCOMPATIBLE_SYSTEM_BUNDLE_VERSION_PAIRS)
def test_incompatible_versions_are_not_accepted(system, bundle) -> None:
    """Test that incompatible versions are not accepted."""
    system_info = KitInfo(name="Astoria Development", version=system)
    bundle_info = load_bundle("valid.toml")
    bundle_info.kit.version = bundle

    with pytest.raises(IncompatibleKitVersionException):
        bundle_info.check_kit_version_is_compatible(system_info)


def test_incompatible_kit_name_is_not_accepted() -> None:
    """Test that incompatible kit names are not accepted."""
    system_info = KitInfo(name="Astoria Development", version="0.0.0.0dev")
    bundle_info = load_bundle("valid.toml")
    bundle_info.kit.name = "Not Astoria Development"

    with pytest.raises(IncompatibleKitVersionException):
        bundle_info.check_kit_version_is_compatible(system_info)


def test_kit_dev_message_is_added_when_dev_build() -> None:
    """Test that the user is warned when using a development build."""
    system_info = KitInfo(name="Astoria Development", version="0.0.0.0dev")
    bundle_info = load_bundle("valid.toml")

    messages = bundle_info.check_kit_version_is_compatible(system_info)
    assert len(messages) == 1
    assert "DEVELOPMENT BUILD" in messages[0]


def test_kit_dev_message_is_not_added_on_prod_build() -> None:
    """Test that the user is warned when using a development build."""
    system_info = KitInfo(name="Astoria Development", version="0.0.0.0")
    bundle_info = load_bundle("valid.toml")

    messages = bundle_info.check_kit_version_is_compatible(system_info)
    assert len(messages) == 0


VERSION_DIFF_MESSAGES = [
    ("0.0.0.0", "0.1.0.0", "kit software is unsupported"),
    ("0.1.0.0", "0.0.0.0", "kit software is unsupported"),
    ("0.1.0.0", "0.2.0.0", "kit software is unsupported"),
    ("0.1.0.1", "0.2.0.1", "kit software is unsupported"),
    ("0.1.0.0", "0.2.0.1", "kit software is unsupported"),
    ("0.1.0.0", "0.2.1.1", "kit software is unsupported"),
    ("0.1.1.0", "0.2.1.1", "kit software is unsupported"),
    ("0.1.1.1", "0.2.1.1", "kit software is unsupported"),
    ("0.0.1.0", "0.0.0.0", "kit software is unsupported"),
    ("0.0.1.1", "0.0.0.0", "kit software is unsupported"),
    ("0.0.0.0", "0.0.1.0", "kit software is unsupported"),
    ("0.0.0.0", "0.0.1.1", "kit software is unsupported"),
    ("0.0.0.1", "0.0.0.0", "kit software which is different than the current version."),
    ("0.0.0.0", "0.0.0.1", "kit software which is different than the current version."),
]


@pytest.mark.parametrize("system,bundle,expected_message", VERSION_DIFF_MESSAGES)
def test_kit_warns_on_version_diff(system, bundle, expected_message) -> None:
    """Test that the user is warned when using a development build."""
    system_info = KitInfo(name="Astoria Development", version=system)
    bundle_info = load_bundle("valid.toml")
    bundle_info.kit.version = bundle

    messages = bundle_info.check_kit_version_is_compatible(system_info)
    assert expected_message in "\n".join(messages)
