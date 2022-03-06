"""Class to determine the type of a disk."""

from pathlib import Path
from typing import Dict

from .constraints import Constraint, FilePresentConstraint, TrueConstraint
from .structs import DiskType


class DiskTypeCalculator:
    """
    Helper class to calculate the DiskType of a given disk drive.

    .. warning:: A disk must only rely on itself and not other disks to determine it
             the type of the disk.
    """

    def calculate(self, path: Path) -> DiskType:
        """
        Calculate the DiskType of a drive given it's mount path.

        :param path: The mount path of the drive.
        :returns: The type of the disk.
        """
        constraints: Dict['DiskType', Constraint] = {
            DiskType.USERCODE: FilePresentConstraint("robot.zip"),
            DiskType.METADATA: FilePresentConstraint("astoria.json"),
            DiskType.UPDATE: FilePresentConstraint("updatefile.txt"),
            DiskType.NOACTION: TrueConstraint(),  # Always match
        }

        for typ, constraint in constraints.items():
            if constraint.matches(path):
                return typ

        raise RuntimeError("Unable to determine type of disk.")  # pragma: nocover
