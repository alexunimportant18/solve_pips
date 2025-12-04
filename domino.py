from collections import namedtuple
Domino = namedtuple('Domino', ('left', 'right'))

Domino.__repr__ = lambda self: f"Domino({self.left} | {self.right})"
Domino.reversed = lambda self: Domino(self.right, self.left) 
Domino.__eq__ = lambda self, other: (self.left == other.left and self.right == other.right) or (self.left == other.right and self.right == other.left)
Domino.__hash__ = lambda self: self.left * 9973 + self.right if self.left < self.right else self.right * 9973 + self.left

def value_distribution(dominoes: list[Domino]) -> dict[int, int]:
    distribution = {}
    for domino in dominoes:
        for value in [domino.left, domino.right]:
            if value not in distribution:
                distribution[value] = 0
            distribution[value] += 1
    return distribution

