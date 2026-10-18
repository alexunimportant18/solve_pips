from enum import Enum

from position import Position


class ConstraintType(Enum):
    """Types of constraints that can be applied to board cells.

    Attributes:
        EQUAL: All cells in the constraint must have the same value.
        TOTAL: The sum of pips in all cells must equal a specific value.
        FREE: No specific constraint on the cell.
        DEAD: The cell is blocked and cannot contain a domino.
        LT: The sum of pips must be less than a specific value.
        GT: The sum of pips must be greater than a specific value.
        NE: All cells in the constraint must have distinct values.
        VALUE: The cell must contain a specific pip value.
    """

    EQUAL = 1
    TOTAL = 2
    FREE = 3
    DEAD = 4
    LT = 5
    GT = 6
    NE = 7
    VALUE = 8


class Constraint:
    """Represents a rule that restricts which values can be placed in specific cells.

    Attributes:
        constraint_type (ConstraintType): The type of rule being applied.
        value (int | None): The target value for the constraint (e.g., the sum for TOTAL).
        positions (list[Position]): The list of board positions affected by this constraint.
    """

    def __init__(
        self,
        constraint_type: ConstraintType,
        positions: list[Position] = [],
        value: int | None = None,
    ):
        """Initializes a Constraint instance.

        Args:
            constraint_type (ConstraintType): The type of the constraint.
            positions (list[Position], optional): The positions the constraint applies to. Defaults to [].
            value (int | None, optional): The value associated with the constraint. Defaults to None.
        """
        self.constraint_type = constraint_type
        self.value = value
        self.positions = positions

    def __repr__(self):
        """Returns a string representation of the constraint.

        Returns:
            str: Formatted string containing type, value, and positions.
        """
        return f"Constraint({self.constraint_type}, {self.value}, {self.positions})"

    def get_restrictiveness(self) -> int:
        """Calculates the restrictiveness of a constraint.

        Args:
            constraint (Constraint): The constraint to evaluate.

        Returns:
            int: The restrictiveness score (lower value is more restrictive).
        """
        if self.constraint_type == ConstraintType.VALUE:
            return 1
        elif self.constraint_type == ConstraintType.EQUAL:
            return 2
        elif self.constraint_type == ConstraintType.TOTAL:
            return 3
        else:
            return 4
