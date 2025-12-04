from enum import Enum

class ConstraintType(Enum):
    EQUAL = 1
    TOTAL = 2
    FREE = 3
    DEAD = 4
    LT = 5
    GT = 6
    NE = 7

class Constraint:
    def __init__(self, constraint_type: ConstraintType, positions: list[tuple[int, int]] = [], value: int | None = None):
        self.constraint_type = constraint_type
        self.value = value
        self.positions = positions

    def __repr__(self):
        return f"Constraint({self.constraint_type}, {self.value}, {self.positions})"

        