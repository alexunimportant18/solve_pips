import pytest
from constraint import Constraint, ConstraintType

def test_constraint_repr():
    """
    Tests the __repr__ method of the Constraint class.
    """
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (0, 1)], 5)
    expected_repr = "Constraint(ConstraintType.TOTAL, 5, [(0, 0), (0, 1)])"
    assert repr(constraint) == expected_repr

    constraint_no_value = Constraint(ConstraintType.EQUAL, [(0, 0), (0, 1)])
    expected_repr_no_value = "Constraint(ConstraintType.EQUAL, None, [(0, 0), (0, 1)])"
    assert repr(constraint_no_value) == expected_repr_no_value