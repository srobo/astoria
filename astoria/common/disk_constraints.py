"""
USB Constraint.

Defines a set of parameters that a USB / Folder can conform to.
"""
from abc import ABCMeta, abstractmethod
from pathlib import Path


class Constraint(metaclass=ABCMeta):
    """A constraint that a path can match."""

    @abstractmethod
    def matches(self, path: Path) -> bool:
        """
        Determine if the disk at the given path matches the constraint.

        :param path: path to the mount point of the disk
        """
        raise NotImplementedError  # pragma: nocover


class FilePresentConstraint(Constraint):
    """
    Ensure that a file is present on the disk.

    This constraint will check that the path exists and contains the given file.
    """

    def __init__(self, filename: str) -> None:
        """
        Initialise the constraint class.

        :param filename: name of the file to find on the disk
        """
        self.filename = filename

    def matches(self, path: Path) -> bool:
        """
        Determine if the disk at the given path matches the constraint.

        :param path: path to the mount point of the disk
        """
        return all([
            path.exists(),
            path.is_dir(),
            path.joinpath(self.filename).exists(),
        ])

    def __repr__(self) -> str:
        return f"FilePresentConstraint(filename={self.filename})"


class NumberOfFilesConstraint(Constraint):
    """
    Ensure that a certain number of files are present.

    This can be used to ensure that there are no spurious files on the disk.
    """

    def __init__(self, n: int):
        """
        Initialise the constraint class.

        :param n: The number of files that should be on the disk.
        """
        self.n = n

    def matches(self, path: Path) -> bool:
        """
        Determine if the disk at the given path matches the constraint.

        :param path: path to the mount point of the disk
        """
        if all([
            path.exists(),
            path.is_dir(),
        ]):
            return self.n == len(list(path.iterdir()))
        else:
            return False

    def __repr__(self) -> str:
        return f"NumberOfFilesConstraint(n={self.n})"


class OrConstraint(Constraint):
    """Ensure that either of the given constraints match."""

    def __init__(self, a: Constraint, b: Constraint) -> None:
        """
        Initialise the constraint class.

        :param a: The first constraint
        :param b: The second constraint
        """
        self.a = a
        self.b = b

    def matches(self, path: Path) -> bool:
        """
        Determine if the disk at the given path matches the constraint.

        :param path: path to the mount point of the disk
        """
        return any([
            self.a.matches(path),
            self.b.matches(path),
        ])

    def __repr__(self) -> str:
        return f"OrConstraint(a={self.a}, b={self.b})"


class AndConstraint(Constraint):
    """Ensure that both of the constraints match."""

    def __init__(self, a: Constraint, b: Constraint) -> None:
        """
        Initialise the constraint class.

        :param a: The first constraint
        :param b: The second constraint
        """
        self.a = a
        self.b = b

    def matches(self, path: Path) -> bool:
        """
        Determine if the disk at the given path matches the constraint.

        :param path: path to the mount point of the disk
        """
        return all([
            self.a.matches(path),
            self.b.matches(path),
        ])

    def __repr__(self) -> str:
        return f"AndConstraint(a={self.a}, b={self.b})"


class NotConstraint(Constraint):
    """Ensure that the constraint does not match."""

    def __init__(self, a: Constraint):
        """
        Initialise the constraint class.

        :param a: The constraint to negate
        """
        self.a = a

    def matches(self, path: Path) -> bool:
        """
        Determine if the disk at the given path matches the constraint.

        :param path: path to the mount point of the disk
        """
        return not self.a.matches(path)

    def __repr__(self) -> str:
        return f"NotConstraint(a={self.a})"


class TrueConstraint(Constraint):
    """
    A constraint that is always true.

    Useful to create a default value when matching disks in order.
    """

    def matches(self, _: Path) -> bool:
        """
        Determine if the disk at the given path matches the constraint.

        :param _: path to the mount point of the disk. Not used.
        """
        return True

    def __repr__(self) -> str:
        return "TrueConstraint()"


class FalseConstraint(Constraint):
    """A constraint that is always false."""

    def matches(self, _: Path) -> bool:
        """
        Determine if the disk at the given path matches the constraint.

        :param _: path to the mount point of the disk. Not used.
        """
        return False

    def __repr__(self) -> str:
        return "FalseConstraint()"
