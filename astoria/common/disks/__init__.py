"""Code for recognising disk drives."""

from .structs import DiskInfo, DiskType, DiskUUID
from .type_calculator import DiskTypeCalculator

__all__ = [
    "DiskInfo",
    "DiskType",
    "DiskTypeCalculator",
    "DiskUUID",
]
