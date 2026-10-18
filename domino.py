from collections import namedtuple

Domino = namedtuple("Domino", ("left", "right"))
Domino.__repr__ = lambda self: f"[{self.left}|{self.right}]"

Domino.__eq__ = lambda self, other: {self.left, self.right} == {other.left, other.right}
Domino.__hash__ = lambda self: hash(frozenset([self.left, self.right]))


def reverse_domino(other: Domino) -> Domino:
    """Returns a new Domino with the left and right values swapped.

    Args:
        other (Domino): The domino to reverse.

    Returns:
        Domino: A new Domino instance with swapped values.
    """
    return Domino(other.right, other.left)


def value_distribution(dominoes: list[Domino]) -> dict[int, int]:
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
