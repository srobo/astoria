"""Class to determine the type of a disk."""

from pathlib import Path
from typing import Dict

from astoria.common.config import NoValidRobotSettingsException, RobotSettings

from .constraints import Constraint, FilePresentConstraint, TrueConstraint
from .structs import DiskType


class DiskTypeCalculator:
    """
    Helper class to calculate the DiskType of a given disk drive.

    .. warning:: A disk must only rely on itself and not other disks to determine it
             the type of the disk.
    """

    def __init__(self, default_usercode_entrypoint: str) -> None:
        """
        Initialise the DiskTypeCalculator.

        :param default_usercode_entrypoint: default entrypoint from astoria config
        """
        self._default_usercode_entrypoint = default_usercode_entrypoint

    def _get_usercode_constraint(self, path: Path) -> Constraint:
        """
        Get the usercode constraint for a disk.

        Calculates the usercode constraint based on the robot settings.

        :param path: The mount path of the disk.
        :returns: The usercode constraint for the disk.
        """
        settings_path = path / "robot-settings.toml"
        if settings_path.exists():
            try:
                settings = RobotSettings.load_settings_file(settings_path)
                return FilePresentConstraint(settings.usercode_entrypoint)
            except NoValidRobotSettingsException:
                pass

        # Fall back to the default if we cannot load the settings
        return FilePresentConstraint(self._default_usercode_entrypoint)

    def calculate(self, path: Path) -> DiskType:
        """
        Calculate the DiskType of a drive given it's mount path.

        :param path: The mount path of the drive.
        :returns: The type of the disk.
        """
        constraints: Dict['DiskType', Constraint] = {
            DiskType.USERCODE: self._get_usercode_constraint(path),
            DiskType.METADATA: FilePresentConstraint("astoria.json"),
            DiskType.UPDATE: FilePresentConstraint("updatefile.txt"),
            DiskType.NOACTION: TrueConstraint(),  # Always match
        }

        for typ, constraint in constraints.items():
            if constraint.matches(path):
                return typ

        raise RuntimeError("Unable to determine type of disk.")  # pragma: nocover
