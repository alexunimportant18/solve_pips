import copy
import logging
from typing import Generator

from termcolor import colored

from combination import Combination
from constraint import Constraint, ConstraintType
from direction import Direction
from domino import Domino, reverse_domino, value_distribution
from position import Position

color_sequence = [
    "red",
    "green",
    "blue",
    "yellow",
    "magenta",
    "cyan",
    "light_red",
    "light_green",
    "light_blue",
]


def get_next_color() -> Generator[str, None, None]:
    """Infinite generator that cycles through the defined color sequence.

    Yields:
        str: The next color string from the color_sequence.
    """
    while True:
        yield from color_sequence


def find_combinations(n: int, t: int) -> list[Combination]:
    """Finds all possible combinations of N numbers (0-6) that sum up to T.

    Args:
        n (int): The number of cells in the combination.
        t (int): The target sum.

    Returns:
        list[Combination]: A list of combinations that sum to T.
    """
    if n * 6 < t or n * 0 > t:
        return []

    def find_combinations_recursive(
        n_rem: int,
        t_rem: int,
        current_combination: Combination,
        result: list[Combination],
    ):
        if n_rem == 0:
            if t_rem == 0:
                result.append(current_combination)
            return

        if t_rem < 0 or n_rem * 6 < t_rem:
            return

        start = current_combination[-1] if current_combination else 0
        for i in range(start, 7):
            find_combinations_recursive(
                n_rem - 1, t_rem - i, current_combination + [i], result
            )

    result: list[Combination] = []
    find_combinations_recursive(n, t, [], result)
    return result


def find_subset_of_possible_dominoes_in_combination(
    combination: Combination, dominoes: set[Domino]
) -> set[Domino]:
    """Finds dominoes that can satisfy the values in a specific combination.

    Args:
        combination (Combination): A list of values that must be filled.
        dominoes (set[Domino]): The set of available dominoes to choose from.

    Returns:
        set[Domino]: The set of dominoes that can be used to form the combination.
    """
    possible_dominoes: set[Domino] = set()
    if len(combination) == 0:
        return possible_dominoes

    value: int = combination[0]
    domino_list = list(dominoes)
    for domino in domino_list:
        if domino.left == value or domino.right == value:
            possible_dominoes.add(domino)
            remaining_dominoes = dominoes - {domino}

            remaining_combination = combination.copy()
            remaining_combination.remove(value)

            other_value = domino.right if domino.left == value else domino.left
            if other_value in remaining_combination:
                remaining_combination.remove(other_value)

            if len(remaining_combination) > 0 and len(remaining_dominoes) > 0:
                possible_dominoes.update(
                    find_subset_of_possible_dominoes_in_combination(
                        remaining_combination, remaining_dominoes
                    )
                )

    return possible_dominoes


def find_possible_dominoes_with_total_count(
    dominoes: set[Domino], count: int, value: int | None
) -> set[Domino]:
    """Finds dominoes that can sum to a specific total given a number of cells.

    Args:
        dominoes (set[Domino]): Available dominoes.
        count (int): Number of cells.
        value (int | None): Target sum.

    Returns:
        set[Domino]: Possible dominoes.

    Raises:
        ValueError: If value is None.
    """
    if value is None:
        raise ValueError("value must be provided")

    result: set[Domino] = set()
    combinations: list[Combination] = find_combinations(count, value)

    for combination in combinations:
        result.update(
            find_subset_of_possible_dominoes_in_combination(combination, dominoes)
        )

    return result


def find_possible_dominoes_with_less_than(
    dominoes: set[Domino], count: int, value: int | None
) -> set[Domino]:
    """Finds dominoes that can sum to less than a specific value.

    Args:
        dominoes (set[Domino]): Available dominoes.
        count (int): Number of cells.
        value (int | None): Threshold value.

    Returns:
        set[Domino]: Possible dominoes.

    Raises:
        ValueError: If value is None.
    """
    if value is None:
        raise ValueError("value must be provided")

    result: set[Domino] = set()
    for i in range(0, value):
        combinations: list[Combination] = find_combinations(count, i)
        for combination in combinations:
            result.update(
                find_subset_of_possible_dominoes_in_combination(combination, dominoes)
            )

    logging.debug(
        f"find_possible_dominoes_with_less_than({dominoes}, {count}, {value}) = {result}"
    )
    return result


def find_possible_dominoes_with_greater_than(
    dominoes: set[Domino], count: int, value: int | None
) -> set[Domino]:
    """Finds dominoes that can sum to more than a specific value.

    Args:
        dominoes (set[Domino], count (int), value (int | None).

    Returns:
        set[Domino]: Possible dominoes.

    Raises:
        ValueError: If value is None.
    """
    if value is None:
        raise ValueError("value must be provided")

    result: set[Domino] = set()
    upperbound: int = count * 6 + 1
    for i in range(value + 1, upperbound):
        combinations: list[Combination] = find_combinations(count, i)
        for combination in combinations:
            result.update(
                find_subset_of_possible_dominoes_in_combination(combination, dominoes)
            )

    return result


def dot_frequency(dominoes: list[Domino], dot: int) -> int:
    result = 0
    for domino in dominoes:
        if domino.left == dot:
            result += 1
        if domino.right == dot:
            result += 1
    return result


class Board:
    """Represents the game board, managing pips, constraints and placements.

    Attributes:
        n_row (int): Total rows.
        n_col (int): Total columns.
        constraint_list (list[Constraint]): All active constraints on the board.
        board (list[list[int | None]]): Grid of pip values.
        constraints (list[list[Constraint]]): Grid of constraints per cell.
        possible_dominoes (list[list[set[Domino]]]): Pre-calculated valid dominoes per cell.
        sorted_positions (list[Position]): Positions sorted by constraint restrictiveness.
        cell_colors (list[list[str]]): Colors assigned to cells for visualization.
        color_index (int): Current index in the color sequence.
    """

    def __init__(self, width: int, height: int):
        """Initializes the Board.

        Args:
            width (int): Number of columns.
            height (int): Number of rows.
        """
        self.n_row = height
        self.n_col = width
        self.constraint_list = []
        self.board: list[list[int | None]] = [
            [None for _ in range(self.n_col)] for _ in range(self.n_row)
        ]
        self.constraints = [
            [
                Constraint(ConstraintType.FREE, [Position(row=row, col=col)], None)
                for col in range(self.n_col)
            ]
            for row in range(self.n_row)
        ]
        self.possible_dominoes = [
            [set() for _ in range(self.n_col)] for _ in range(self.n_row)
        ]
        self.sorted_positions: list[Position] = []
        self.cell_colors: list[list[str]] = [
            ["white" for _ in range(self.n_col)] for _ in range(self.n_row)
        ]
        self.color_index = 0

    def sort_constraints(self) -> None:
        """Sorts the constraints by restrictiveness."""
        self.constraint_list.sort(key=lambda x: x.get_restrictiveness())

    def add_constraint(self, constraint: Constraint) -> None:
        """Adds a puzzle constraint to the board.

        Args:
            constraint (Constraint): The constraint object to add.

        Raises:
            ValueError: If a position in the constraint is already occupied.
        """
        for position in constraint.positions:
            if self.board[position.row][position.col] is not None:
                raise ValueError(f"Position {position} is already occupied")

        match constraint.constraint_type:
            case ConstraintType.DEAD:
                for position in constraint.positions:
                    self.board[position.row][position.col] = -1
                    self.constraints[position.row][position.col] = Constraint(
                        ConstraintType.DEAD, constraint.positions, -1
                    )

            case (
                ConstraintType.EQUAL
                | ConstraintType.NE
                | ConstraintType.TOTAL
                | ConstraintType.LT
                | ConstraintType.GT
            ):
                for position in constraint.positions:
                    self.constraints[position.row][position.col] = Constraint(
                        constraint.constraint_type,
                        constraint.positions,
                        constraint.value,
                    )

            case ConstraintType.FREE:
                for position in constraint.positions:
                    self.constraints[position.row][position.col] = Constraint(
                        ConstraintType.FREE,
                        constraint.positions,
                        None,
                    )

            case ConstraintType.VALUE:
                for position in constraint.positions:
                    self.constraints[position.row][position.col] = Constraint(
                        ConstraintType.VALUE,
                        constraint.positions,
                        constraint.value,
                    )

        self.constraint_list.append(constraint)

    def cell(self, row: int, col: int) -> int | None:
        """Returns the value of a specific cell.

        Args:
            row (int): Row index.
            col (int): Column index.

        Returns:
            int | None: Pip value or None if empty.
        """
        return self.board[row][col]

    def generate_possible_dominoes(self, available_dominoes: set[Domino]):
        """Pre-calculates which dominoes can fit into each cell based on constraints.

        Args:
            available_dominoes (set[Domino]): The set of dominoes currently in hand.
        """
        distribution: dict[int, int] = value_distribution(list(available_dominoes))
        logging.debug(f"{distribution=}")

        for constraint in self.constraint_list:
            match constraint.constraint_type:
                case ConstraintType.FREE | ConstraintType.NE:
                    for position in constraint.positions:
                        self.possible_dominoes[position.row][position.col] = set(
                            available_dominoes
                        )

                case ConstraintType.VALUE:
                    for position in constraint.positions:
                        possible_dominoes = set()
                        for domino in available_dominoes:
                            if (
                                domino.left == constraint.value
                                or domino.right == constraint.value
                            ):
                                possible_dominoes.add(domino)
                        self.possible_dominoes[position.row][position.col] = (
                            possible_dominoes
                        )

                case ConstraintType.EQUAL:
                    minimum_count = len(constraint.positions)
                    result = set()
                    for i in range(0, 7):
                        if i in distribution.keys():
                            if distribution[i] >= minimum_count:
                                for domino in available_dominoes:
                                    if domino.left == i or domino.right == i:
                                        result.add(domino)

                    for position in constraint.positions:
                        self.possible_dominoes[position.row][position.col] = result

                case ConstraintType.TOTAL:
                    count = len(constraint.positions)
                    value = constraint.value
                    result = find_possible_dominoes_with_total_count(
                        available_dominoes, count, value
                    )
                    for position in constraint.positions:
                        self.possible_dominoes[position.row][position.col] = result

                case ConstraintType.LT:
                    count: int = len(constraint.positions)
                    value: int | None = constraint.value
                    result: set[Domino] = find_possible_dominoes_with_less_than(
                        available_dominoes, count, value
                    )
                    for position in constraint.positions:
                        self.possible_dominoes[position.row][position.col] = result

                case ConstraintType.GT:
                    count: int = len(constraint.positions)
                    value: int | None = constraint.value
                    result: set[Domino] = find_possible_dominoes_with_greater_than(
                        available_dominoes, count, value
                    )
                    for position in constraint.positions:
                        self.possible_dominoes[position.row][position.col] = result

                case ConstraintType.DEAD:
                    for position in constraint.positions:
                        self.possible_dominoes[position.row][position.col] = set()

        self.sort_positions()
        starts_from = 0
        for i, position in enumerate(self.sorted_positions):
            if self.cell(position.row, position.col) is None:
                starts_from = i
                break
        self.sorted_positions = self.sorted_positions[starts_from:]

    def place_domino(
        self,
        domino: Domino,
        position: Position,
        direction: Direction,
        available_dominoes: list[Domino],
        domino_to_remove: Domino,
    ) -> bool:
        """Tries to place a domino on the board at a given position and direction.

        Args:
            domino (Domino): The domino to place.
            position (Position): The starting cell.
            direction (Direction): The direction of the second cell.

        Returns:
            bool: True if placed successfully, False otherwise.
        """
        row1, col1 = position.row, position.col
        if not (0 <= row1 < self.n_row and 0 <= col1 < self.n_col):
            logging.debug(f"Start position {position} is out of bounds")
            return False

        if self.board[row1][col1] is not None:
            logging.debug(f"Position {position} is already occupied")
            return False

        if (
            domino not in self.possible_dominoes[row1][col1]
            # and reverse_domino(domino) not in self.possible_dominoes[row1][col1]
        ):
            logging.debug(f"Domino {domino} is not possible at {position}")
            return False

        row2, col2 = position.row, position.col
        if direction == Direction.NORTH:
            row2 -= 1
        elif direction == Direction.EAST:
            col2 += 1
        elif direction == Direction.SOUTH:
            row2 += 1
        elif direction == Direction.WEST:
            col2 -= 1

        if not (0 <= row2 < self.n_row and 0 <= col2 < self.n_col):
            logging.debug(f"Domino {domino} is out of bounds at {position} {direction}")
            return False

        if self.board[row2][col2] is not None:
            logging.debug(f"Position {(row2, col2)} is already occupied")
            return False

        if (
            domino not in self.possible_dominoes[row2][col2]
            # and reverse_domino(domino) not in self.possible_dominoes[row2][col2]
        ):
            logging.debug(f"Domino {domino} is not possible at {(row2, col2)}")
            return False

        # Save original values before modification
        orig_board1 = self.board[row1][col1]
        orig_board2 = self.board[row2][col2]
        orig_color1 = self.cell_colors[row1][col1]
        orig_color2 = self.cell_colors[row2][col2]
        orig_color_index = self.color_index

        current_color = color_sequence[self.color_index]
        self.board[row1][col1] = domino.left
        self.board[row2][col2] = domino.right
        self.cell_colors[row1][col1] = current_color
        self.cell_colors[row2][col2] = current_color
        self.color_index = (self.color_index + 1) % len(color_sequence)

        remaining_dominoes = [
            item for item in available_dominoes if item != domino_to_remove
        ]
        # remaining_dominoes = available_dominoes
        if remaining_dominoes:
            if not self.check_partial_constraints(remaining_dominoes):
                logging.debug(
                    f"Domino {domino} violates partial constraints at {position} {direction}"
                )
                # Restore original values instead of using deepcopy
                self.board[row1][col1] = orig_board1
                self.board[row2][col2] = orig_board2
                self.cell_colors[row1][col1] = orig_color1
                self.cell_colors[row2][col2] = orig_color2
                self.color_index = orig_color_index
                return False

        logging.debug(f"Domino {domino} placed at {position} {direction}")
        return True

    def sort_positions(self):
        """Sorts all board positions by the number of possible dominoes (most constrained first)."""
        self.sorted_positions = [
            Position(row=i, col=j) for i in range(self.n_row) for j in range(self.n_col)
        ]
        self.sorted_positions.sort(
            key=lambda x: (len(self.possible_dominoes[x.row][x.col]), x.row, x.col)
        )

    def find_next_empty_cell(self) -> Position | None:
        """Finds the next empty cell based on sorted positions.

        Returns:
            Position | None: The next Position to fill, or None if the board is full.
        """
        for position in self.sorted_positions:
            if self.cell(position.row, position.col) is None:
                return position
        return None

    def _check_constraint(
        self,
        constraint: Constraint,
        available_dominoes: list[Domino],
        is_partial: bool,
    ) -> bool:
        """Internal method to check if a single constraint is satisfied.

        Args:
            constraint (Constraint): The constraint to check.
            is_partial (bool): If True, checks if the constraint can still be satisfied.

        Returns:
            bool: True if satisfied/possible, False otherwise.
        """
        match constraint.constraint_type:
            case ConstraintType.FREE:
                return True

            case ConstraintType.VALUE:
                if constraint.value is None:
                    raise ValueError("value must be provided")

                for position in constraint.positions:
                    cell_value = self.board[position.row][position.col]
                    if cell_value is not None:
                        if cell_value != constraint.value:
                            return False

            case ConstraintType.DEAD:
                for position in constraint.positions:
                    if self.board[position.row][position.col] != -1:
                        return False

            case ConstraintType.EQUAL:
                value = None
                need_to_fill = 0
                for position in constraint.positions:
                    cell_value = self.board[position.row][position.col]
                    if cell_value is not None:
                        if value is None:
                            value = cell_value
                        elif cell_value != value:
                            return False
                    else:
                        need_to_fill += 1
                if value:
                    if need_to_fill > dot_frequency(available_dominoes, value):
                        return False

            case ConstraintType.NE:
                value_set = set()
                for position in constraint.positions:
                    cell_value = self.board[position.row][position.col]
                    if cell_value is not None:
                        if cell_value in value_set:
                            return False
                        value_set.add(cell_value)

            case ConstraintType.TOTAL:
                if constraint.value is None:
                    raise ValueError("value must be provided")

                total = 0
                is_complete = True
                for position in constraint.positions:
                    value = self.board[position.row][position.col]
                    if value is not None:
                        total += value
                    else:
                        is_complete = False

                if is_partial:
                    if total > constraint.value:
                        return False
                    if is_complete and total != constraint.value:
                        return False
                else:
                    if total > constraint.value:
                        return False
                    if total != constraint.value:
                        return False

            case ConstraintType.LT:
                if constraint.value is None:
                    raise ValueError("value must be provided")

                total = 0
                for position in constraint.positions:
                    value = self.board[position.row][position.col]
                    if value is not None:
                        total += value
                if total >= constraint.value:
                    return False

            case ConstraintType.GT:
                if constraint.value is None:
                    raise ValueError("value must be provided")

                total = 0
                empty_cells = 0
                is_complete = True
                for position in constraint.positions:
                    value = self.board[position.row][position.col]
                    if value is not None:
                        total += value
                    else:
                        empty_cells += 1
                        is_complete = False

                if is_complete:
                    if total <= constraint.value:
                        return False
                else:
                    max_possible_total = total + (empty_cells * 6)
                    if max_possible_total <= constraint.value:
                        return False

            case _:
                raise ValueError(
                    f"Unknown constraint type: {constraint.constraint_type}"
                )

        return True

    def check_partial_constraints(self, available_dominoes: list[Domino]):
        """Checks if current placements do not yet violate any constraints.

        Returns:
            bool: True if no violations found, False otherwise.
        """
        for constraint in self.constraint_list:
            if not self._check_constraint(
                constraint, available_dominoes, is_partial=True
            ):
                return False
        return True

    def __repr__(self):
        """Returns a colored string representation of the board.

        Returns:
            str: The visualized grid.
        """
        result = ""
        for i, row in enumerate(self.board):
            colored_cells = []
            for j, cell in enumerate(row):
                if cell == -1:
                    colored_cells.append("  ")
                elif cell is not None:
                    colored_cells.append(colored(f"{cell:>2}", self.cell_colors[i][j]))
                else:
                    colored_cells.append(" .")
            result += "|" + "|".join(colored_cells) + "|\n"
        return result

    def print_possible_dominoes(self):
        """Prints the possible dominoes for each cell to the console."""
        for i, row in enumerate(self.possible_dominoes):
            for j, col in enumerate(row):
                print(f"{i},{j}: {col}")

    def print_constraints(self):
        """Prints a visualization of the board's constraints.

        Colors are used to group cells belonging to the same constraint.
        """
        color_generator = get_next_color()
        board_constraints = [
            [(" . ", "white") for _ in range(self.n_col)] for _ in range(self.n_row)
        ]
        for constraint in self.constraint_list:
            match constraint.constraint_type:
                case ConstraintType.FREE:
                    for position in constraint.positions:
                        board_constraints[position.row][position.col] = (
                            " . ",
                            "white",
                        )

                case ConstraintType.VALUE:
                    for position in constraint.positions:
                        board_constraints[position.row][position.col] = (
                            f"{constraint.value:3d}",
                            "white",
                        )

                case ConstraintType.DEAD:
                    for position in constraint.positions:
                        board_constraints[position.row][position.col] = (" X ", "white")

                case ConstraintType.EQUAL:
                    current_color = next(color_generator)
                    for position in constraint.positions:
                        board_constraints[position.row][position.col] = (
                            " = ",
                            current_color,
                        )

                case ConstraintType.NE:
                    current_color = next(color_generator)
                    for position in constraint.positions:
                        board_constraints[position.row][position.col] = (
                            " ! ",
                            current_color,
                        )

                case ConstraintType.LT:
                    current_color = next(color_generator)
                    for position in constraint.positions:
                        board_constraints[position.row][position.col] = (
                            f"<{constraint.value:2d}",
                            current_color,
                        )

                case ConstraintType.GT:
                    current_color = next(color_generator)
                    for position in constraint.positions:
                        board_constraints[position.row][position.col] = (
                            f">{constraint.value:2d}",
                            current_color,
                        )

                case ConstraintType.TOTAL:
                    current_color = next(color_generator)
                    for position in constraint.positions:
                        board_constraints[position.row][position.col] = (
                            f"+{constraint.value:2d}",
                            current_color,
                        )

        for row in board_constraints:
            print("|" + "|".join([colored(cell, color) for cell, color in row]) + "|")

    def print_board(self):
        """Prints the current board state to the console."""
        print(self.__repr__())

    def __hash__(self):
        """Computes a hash based on the current pip values of the board.

        Returns:
            int: Hash value.
        """
        board_tuple = tuple(tuple(row) for row in self.board)
        return hash(board_tuple)

    def __eq__(self, other):
        """Checks if two boards are identical in state.

        Args:
            other (object): The board to compare with.

        Returns:
            bool: True if states match, False otherwise.
        """
        if not isinstance(other, Board):
            return False
        return self.board == other.board
