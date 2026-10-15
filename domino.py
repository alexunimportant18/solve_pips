from collections import namedtuple

Domino = namedtuple("Domino", ("left", "right"))
Domino.__repr__ = lambda self: f"[{self.left}|{self.right}]"

Domino.__eq__ = lambda self, other: {self.left, self.right} == {other.left, other.right}
Domino.__hash__ = lambda self: hash(frozenset([self.left, self.right]))


def reverse_domino(other: Domino):
    return Domino(other.right, other.left)


def value_distribution(dominoes: list[Domino]) -> dict[int, int]:
    distribution = {}
    for domino in dominoes:
        for value in [domino.left, domino.right]:
            if value not in distribution:
                distribution[value] = 0
            distribution[value] += 1
    return distribution
