import pytest

from constraint import Constraint, ConstraintType
from position import Position


def test_constraint_initialization():
    """Test that Constraint initializes correctly with all attributes."""
    positions = [Position(row=0, col=0), Position(row=0, col=1)]
    constraint = Constraint(ConstraintType.TOTAL, positions, 5)

    assert constraint.constraint_type == ConstraintType.TOTAL
    assert constraint.value == 5
    assert constraint.positions == positions


def test_constraint_repr():
    """Test that __repr__ returns the expected string representation."""
    positions = [Position(row=0, col=0)]
    constraint = Constraint(ConstraintType.DEAD, positions)

    repr_str = repr(constraint)
    assert "Constraint(" in repr_str
    assert "ConstraintType.DEAD" in repr_str
    assert "None" in repr_str  # value is None
    assert "row=0" in repr_str
    assert "col=0" in repr_str


def test_get_restrictiveness_value():
    """Test that VALUE constraint has the highest restrictiveness (lowest score)."""
    constraint = Constraint(ConstraintType.VALUE, [Position(row=0, col=0)], 3)
    assert constraint.get_restrictiveness() == 1


def test_get_restrictiveness_equal():
    """Test that EQUAL constraint has the second highest restrictiveness."""
    positions = [Position(row=0, col=0), Position(row=0, col=1)]
    constraint = Constraint(ConstraintType.EQUAL, positions)
    assert constraint.get_restrictiveness() == 2


def test_get_restrictiveness_total():
    """Test that TOTAL constraint has the third highest restrictiveness."""
    positions = [Position(row=0, col=0), Position(row=0, col=1)]
    constraint = Constraint(ConstraintType.TOTAL, positions, 5)
    assert constraint.get_restrictiveness() == 3


def test_get_restrictiveness_other_types():
    """Test that all other constraint types have the lowest restrictiveness."""
    # Test all other constraint types return 4
    test_constraints = [
        Constraint(ConstraintType.FREE, [Position(row=0, col=0)]),
        Constraint(ConstraintType.DEAD, [Position(row=0, col=0)]),
        Constraint(
            ConstraintType.LT, [Position(row=0, col=0), Position(row=0, col=1)], 5
        ),
        Constraint(
            ConstraintType.GT, [Position(row=0, col=0), Position(row=0, col=1)], 3
        ),
        Constraint(ConstraintType.NE, [Position(row=0, col=0), Position(row=0, col=1)]),
    ]

    for constraint in test_constraints:
        assert constraint.get_restrictiveness() == 4, (
            f"Failed for {constraint.constraint_type}"
        )


def test_constrainttype_enum_values():
    """Test that all ConstraintType enum members have the expected integer values."""
    assert ConstraintType.EQUAL.value == 1
    assert ConstraintType.TOTAL.value == 2
    assert ConstraintType.FREE.value == 3
    assert ConstraintType.DEAD.value == 4
    assert ConstraintType.LT.value == 5
    assert ConstraintType.GT.value == 6
    assert ConstraintType.NE.value == 7
    assert ConstraintType.VALUE.value == 8


def test_empty_positions_list():
    """Test that Constraint initializes correctly with empty positions list."""
    constraint = Constraint(ConstraintType.FREE)
    assert constraint.positions == []
    assert constraint.value is None
    assert constraint.constraint_type == ConstraintType.FREE
