"""
Usercode strategy.

A usercode strategy defines a matcher for usercode in a folder.

It is used for detecting the usercode drives in astdiskd, and then copying
it into the temporary directory for execution in astprocd.
"""

from abc import abstractmethod
from typing import Union

from pydantic import BaseModel, validator


class BaseUsercodeStrategy(BaseModel):
    """
    A usercode strategy defines how usercode is loaded from a USB drive.

    The `strategy` attribute needs to be unique per class, and allows pydantic
    to unique identify a strategy when parsing it. This means that we can directly
    load the correct strategy in the parsing stage.
    """

    strategy: str  # Pydantic uses this to identify the class.

    @classmethod
    @abstractmethod
    def get_strategy_name(cls) -> str:
        """
        The name of this usercode strategy.

        :returns: name of the usercode strategy.
        """
        raise NotImplementedError  # pragma: nocover

    @validator("strategy")
    def check_strategy_name(cls, v: str) -> str:
        """
        Validate the name of the strategy.

        This is used to tell pydantic to try the next strategy in the union.
        """
        if v != cls.get_strategy_name():
            raise ValueError("Strategy name did not match.")
        return v


class FolderUsercodeStrategy(BaseUsercodeStrategy):
    """
    Code in the folder / USB drive directly.

    i.e a main.py on the USB drive is executed.
    """

    @classmethod
    def get_strategy_name(self) -> str:
        """
        The name of this usercode strategy.

        :returns: name of the usercode strategy.
        """
        return "folder"


class ZipBundleUsercodeStrategy(BaseUsercodeStrategy):
    """Code is contained with a ZIP archive."""

    zip_name: str = "robot.zip"

    @classmethod
    def get_strategy_name(self) -> str:
        """
        The name of this usercode strategy.

        :returns: name of the usercode strategy.
        """
        return "zip_bundle"

    @validator("zip_name")
    def check_zip_file_has_extension(cls, v: str) -> str:
        """Check that the zip file has a .zip extension."""
        if not v.endswith(".zip"):
            raise ValueError(f"Zip Name {v} does not end with .zip")
        return v


UsercodeStrategy = Union[FolderUsercodeStrategy, ZipBundleUsercodeStrategy]
