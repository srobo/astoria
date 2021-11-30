"""Test usercode strategy parsing."""
import unittest

from pydantic import parse_obj_as
from pydantic.error_wrappers import ValidationError

from astoria.common.usercode_strategy import UsercodeStrategy


class TestUsercodeStrategyParsing(unittest.TestCase):
    """Test that we parse the usercode strategies correctly."""

    def test_empty_config(self) -> None:
        """Test that we do not accept an empty config."""
        with self.assertRaises(ValidationError):
            parse_obj_as(UsercodeStrategy, {})

    def test_folder_config(self) -> None:
        """Test that we correctly parse a folder config."""
        strat = parse_obj_as(UsercodeStrategy, {"strategy": "folder"})
        self.assertEqual(strat.strategy, "folder")

    def test_zip_bundle_config(self) -> None:
        """Test that we correctly parse a zip_bundle config."""
        strat = parse_obj_as(
            UsercodeStrategy,
            {"strategy": "zip_bundle", "zip_name": "my_robot.zip"},
        )
        self.assertEqual(strat.strategy, "zip_bundle")
        self.assertEqual(strat.zip_name, "my_robot.zip")

    def test_zip_bundle_config_missing_zip_name(self) -> None:
        """Test that we fall back to robot.zip if not specified."""
        strat = parse_obj_as(UsercodeStrategy, {"strategy": "zip_bundle"})
        self.assertEqual(strat.strategy, "zip_bundle")
        self.assertEqual(strat.zip_name, "robot.zip")

    def test_zip_bundle_config_invalid_zip_name(self) -> None:
        """Test that we do not accept files that don't end with .zip."""
        with self.assertRaisesRegex(
            ValidationError,
            "Zip Name my_robot.tar does not end with .zip",
        ):
            parse_obj_as(
                UsercodeStrategy,
                {"strategy": "zip_bundle", "zip_name": "my_robot.tar"},
            )
