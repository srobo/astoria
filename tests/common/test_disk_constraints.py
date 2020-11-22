"""Test the constraints classes."""

from pathlib import Path

from astoria.common.disk_constraints import (
    AndConstraint,
    Constraint,
    FalseConstraint,
    FilePresentConstraint,
    NotConstraint,
    NumberOfFilesConstraint,
    OrConstraint,
    TrueConstraint,
)

DATA_PATH = Path("tests/data/constraints")

EMPTY_PATH = DATA_PATH.joinpath("empty")
NOT_EXIST_PATH = DATA_PATH.joinpath("does_not_exist")
FILE_PATH = DATA_PATH.joinpath("actually_a_file")

FILE_PRESENT_PATH = DATA_PATH.joinpath("file_present")
THREE_PRESENT_PATH = DATA_PATH.joinpath("three_files_present")
OTHER_PRESENT_PATH = DATA_PATH.joinpath("other_file_present")


def test_subclass() -> None:
    """Test that we can make a subclass of constraint."""
    class TestConstraint(Constraint):
        """A test constraint."""

        def matches(self, path: Path) -> bool:
            """Return true if path matches the constraint."""
            return True

    test_constraint = TestConstraint()
    assert issubclass(TestConstraint, Constraint)
    assert isinstance(test_constraint, TestConstraint)
    assert test_constraint.matches(Path())


def test_file_present_constraint() -> None:
    """Test that the FilePresentConstraint works as expected."""
    constraint = FilePresentConstraint("test.txt")

    assert not constraint.matches(EMPTY_PATH)
    assert not constraint.matches(FILE_PATH)
    assert not constraint.matches(OTHER_PRESENT_PATH)
    assert not constraint.matches(NOT_EXIST_PATH)
    assert constraint.matches(FILE_PRESENT_PATH)

    assert repr(constraint) == "FilePresentConstraint(filename=test.txt)"


def test_number_of_files_constraint() -> None:
    """Test that the NumberOfFilesConstraint works as expected."""
    constraint = NumberOfFilesConstraint(3)
    assert not constraint.matches(EMPTY_PATH)
    assert not constraint.matches(FILE_PATH)
    assert not constraint.matches(OTHER_PRESENT_PATH)
    assert not constraint.matches(NOT_EXIST_PATH)

    assert constraint.matches(THREE_PRESENT_PATH)

    assert repr(constraint) == "NumberOfFilesConstraint(n=3)"


def test_true_constraint() -> None:
    """Test that the TrueConstraint works as expected."""
    constraint = TrueConstraint()

    assert constraint.matches(DATA_PATH)
    assert constraint.matches(EMPTY_PATH)
    assert constraint.matches(NOT_EXIST_PATH)
    assert constraint.matches(FILE_PATH)
    assert constraint.matches(FILE_PRESENT_PATH)
    assert constraint.matches(OTHER_PRESENT_PATH)
    assert constraint.matches(THREE_PRESENT_PATH)

    assert repr(constraint) == "TrueConstraint()"


def test_false_constraint() -> None:
    """Test that the FalseConstraint works as expected."""
    constraint = FalseConstraint()

    assert not constraint.matches(DATA_PATH)
    assert not constraint.matches(EMPTY_PATH)
    assert not constraint.matches(NOT_EXIST_PATH)
    assert not constraint.matches(FILE_PATH)
    assert not constraint.matches(FILE_PRESENT_PATH)
    assert not constraint.matches(OTHER_PRESENT_PATH)
    assert not constraint.matches(THREE_PRESENT_PATH)

    assert repr(constraint) == "FalseConstraint()"


def test_not_constraint() -> None:
    """Test that the NotConstraint works as expected."""
    constraint = NotConstraint(TrueConstraint())
    assert not constraint.matches(NOT_EXIST_PATH)

    assert repr(constraint) == "NotConstraint(a=TrueConstraint())"


def test_or_constraint() -> None:
    """Test that the OrConstraint works as expected."""
    true = TrueConstraint()
    false = NotConstraint(TrueConstraint())
    assert not OrConstraint(false, false).matches(NOT_EXIST_PATH)
    assert OrConstraint(false, true).matches(NOT_EXIST_PATH)
    assert OrConstraint(true, false).matches(NOT_EXIST_PATH)
    assert OrConstraint(true, true).matches(NOT_EXIST_PATH)

    constraint = OrConstraint(true, false)
    assert repr(constraint) == \
        "OrConstraint(a=TrueConstraint(), b=NotConstraint(a=TrueConstraint()))"


def test_and_constraint() -> None:
    """Test that the AndConstraint works as expected."""
    true = TrueConstraint()
    false = NotConstraint(TrueConstraint())
    assert not AndConstraint(false, false).matches(NOT_EXIST_PATH)
    assert not AndConstraint(false, true).matches(NOT_EXIST_PATH)
    assert not AndConstraint(true, false).matches(NOT_EXIST_PATH)
    assert AndConstraint(true, true).matches(NOT_EXIST_PATH)

    constraint = AndConstraint(true, false)
    assert repr(constraint) == \
        "AndConstraint(a=TrueConstraint(), b=NotConstraint(a=TrueConstraint()))"
