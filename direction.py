from enum import Enum, auto

class Direction(Enum):
    """Enumeration of possible directions for domino placement on the grid.
    
    Attributes:
        NORTH: Upward placement.
        EAST: Rightward placement.
        SOUTH: Downward placement.
        WEST: Leftward placement.
    """
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()
