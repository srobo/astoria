"""
Drive class.

Contains no daemon or api specific code.
"""
from pathlib import Path

from pydantic import BaseModel


class Drive(BaseModel):
    """A drive that is present on the system."""

    mount_path: Path
