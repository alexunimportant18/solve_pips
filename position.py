from collections import namedtuple

from pydantic import BaseModel


class Position(BaseModel):
    row: int
    col: int

    def __hash__(self):
        return self.row * 9973 + self.col

    def __eq__(self, other) -> bool:
        return self.row == other.row and self.col == other.col

    def __repr__(self) -> str:
        return super().__repr__()
