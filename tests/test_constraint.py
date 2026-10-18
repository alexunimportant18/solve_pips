import pytest

from constraint import Constraint, ConstraintType
from position import Position


def test_constraint_repr():
    """
    Tests the __repr__ method of the Constraint class.
    """
    constraint = Constraint(
        ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    expected_repr = "Constraint(ConstraintType.TOTAL, 5, [Position(row=0, col=0), Position(row=0, col=1)])"
    assert repr(constraint) == expected_repr

    constraint_no_value = Constraint(
        ConstraintType.EQUAL, [Position(row=0, col=0), Position(row=0, col=1)]
    )
    expected_repr_no_value = "Constraint(ConstraintType.EQUAL, None, [Position(row=0, col=0), Position(row=0, col=1)])"
    assert repr(constraint_no_value) == expected_repr_no_value
