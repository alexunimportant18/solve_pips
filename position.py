from collections import namedtuple

from pydantic import BaseModel


class Position(BaseModel):
    """Represents a coordinate position on the game board.

    Attributes:
        row (int): The row index of the position.
        col (int): The column index of the position.
    """
    row: int
    col: int

    def __hash__(self):
        """Computes a hash value for the position based on row and column.

        Returns:
            int: A hash value.
        """
        return self.row * 9973 + self.col

    def __eq__(self, other) -> bool:
        """Checks if two positions are identical.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if row and col are equal, False otherwise.
        """
        return self.row == other.row and self.col == other.col

    def __repr__(self) -> str:
        """Returns a string representation of the position.

        Returns:
            str: The pydantic representation of the position.
        """
        return super().__repr__()
