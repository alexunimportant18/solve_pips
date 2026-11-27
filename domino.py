from collections import namedtuple
from enum import Enum

Domino = namedtuple("Domino", ("left", "right"))
Domino.__repr__ = lambda self: f"[{self.left}|{self.right}]"


def __eq__(self: Domino, other: object) -> bool:
    if not isinstance(other, Domino):
        return NotImplemented
    return {self.left, self.right} == {other.left, other.right}


Domino.__eq__ = __eq__


def __hash__(self: Domino) -> int:
    return hash(frozenset([self.left, self.right]))


Domino.__hash__ = __hash__


class Side(Enum):
    LEFT = 1
    RIGHT = 2


def reverse_domino(domino: Domino) -> Domino:
    """Returnsverses the order of the pips in a domino.

    Args:
        domino (Domino): The domino to reverse.

    Returns:
        Domino: The reversed domino.
    """
    return Domino(domino.right, domino.left)


def value_distribution(dominoes: set[Domino]) -> dict[int, int]:
    """Calculates the total count of each pip value across a set of dominoes.

    Args:
        dominoes (list[Domino]): A list of dominoes to analyze.

    Returns:
        dict[int, int]: A dictionary where keys are pip values (0-6) and
            values are the number of times that pip appears.
    """
    distribution = {}
    for domino in dominoes:
        for value in [domino.left, domino.right]:
            if value not in distribution:
                distribution[value] = 0
            distribution[value] += 1
    return distribution
