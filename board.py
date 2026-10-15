import copy
import logging
from typing import Generator

from termcolor import colored

from combination import Combination
from constraint import Constraint, ConstraintType
from direction import Direction
from domino import Domino, reverse_domino, value_distribution
from position import Position


def get_next_color() -> Generator[str, None, None]:
    color_code = [
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
    while True:
        yield from color_code


def find_combinations(n: int, t: int) -> list[Combination]:
    """
    Finds all possible combinations of N numbers (0-6) that sum up to T.

    Args:
        n: The number of boxes (or numbers in a combination).
        t: The target sum.

    Returns:
        A list of lists, where each inner list is a combination of numbers
        that sums to T.
    """
    if n * 6 < t or n * 0 > t:
        return []

    # the result will be updated as a side effect
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

        # Optimization: Prune branches that can't possibly reach the target sum.
        if t_rem < 0 or n_rem * 6 < t_rem:
            return

        # since we start from the lowest domino point, we can skip the numbers that are already in the combination
        # by starting from the last found domino point
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
    """
    Finds all dominoes that have at least one number in the given combination.

    Args:
        combination: A list of numbers.
        dominoes: A set of available dominoes.

    Returns:
        A set of dominoes that have at least one number in the combination.
    """
    possible_dominoes: set[Domino] = set()
    if len(combination) == 0:
        return possible_dominoes

    value: int = combination[0]
    for domino in dominoes:
        temp: set[Domino] = copy.deepcopy(dominoes)
        # only one side of the domino in the combination is already enough, maybe the other side is not
        # in the current constraint
        if domino.left == value or domino.right == value:
            possible_dominoes.add(domino)
            temp.remove(domino)
            if len(temp) > 0:
                possible_dominoes.update(
                    find_subset_of_possible_dominoes_in_combination(
                        combination[1:], temp
                    )
                )

    return possible_dominoes


def find_possible_dominoes_with_total_count(
    dominoes: set[Domino], count: int, value: int | None
) -> set[Domino]:
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


class Board:
    def __init__(self, width: int, height: int):
        """
        Initializes the game board.

        Args:
            width (int): The number of columns on the board.
            height (int): The number of rows on the board.

        Attributes:
            n_row (int): The number of rows.
            n_col (int): The number of columns.
            constraints (list[Constraint]): A list of constraints applied to the board.
            board (list[list[int | None]]): A 2D list representing the board state,
                where each cell contains a number (0-6) or None if empty. -1 represents
                a dead cell.
            state (list[list[tuple[ConstraintType, any]]]): A 2D list storing the
                constraint type and value for each cell.
            possible_dominoes (list[list[set[Domino]]]): A 2D list where each cell
                contains a set of dominoes that could potentially be placed there.
            sorted_positions (list[tuple[int, int]]): A list of all board positions,
                sorted by the number of possible dominoes for that position.
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

    def add_constraint(self, constraint: Constraint) -> None:
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
        return self.board[row][col]

    def generate_possible_dominoes(self, availabe_dominoes: set[Domino]):
        distribution: dict[int, int] = value_distribution(list(availabe_dominoes))
        logging.debug(f"{distribution=}")

        for constraint in self.constraint_list:
            match constraint.constraint_type:
                case ConstraintType.FREE | ConstraintType.NE:
                    for position in constraint.positions:
                        self.possible_dominoes[position.row][position.col] = set(
                            availabe_dominoes
                        )

                case ConstraintType.VALUE:
                    for position in constraint.positions:
                        possible_dominoes = set()
                        for domino in availabe_dominoes:
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
                    # find all values that has at least the minimum count
                    result = set()
                    for i in range(0, 7):
                        if i in distribution.keys():
                            if distribution[i] >= minimum_count:
                                for domino in availabe_dominoes:
                                    if domino.left == i or domino.right == i:
                                        result.add(domino)

                    for position in constraint.positions:
                        self.possible_dominoes[position.row][position.col] = result

                case ConstraintType.TOTAL:
                    count = len(constraint.positions)
                    value = constraint.value
                    result = find_possible_dominoes_with_total_count(
                        availabe_dominoes, count, value
                    )
                    for position in constraint.positions:
                        self.possible_dominoes[position.row][position.col] = result

                case ConstraintType.LT:
                    count: int = len(constraint.positions)
                    value: int | None = constraint.value
                    result: set[Domino] = find_possible_dominoes_with_less_than(
                        availabe_dominoes, count, value
                    )
                    for position in constraint.positions:
                        self.possible_dominoes[position.row][position.col] = result

                case ConstraintType.GT:
                    count: int = len(constraint.positions)
                    value: int | None = constraint.value
                    result: set[Domino] = find_possible_dominoes_with_greater_than(
                        availabe_dominoes, count, value
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
        self, domino: Domino, position: Position, direction: Direction
    ) -> bool:
        """
        Tries to place a domino on the board at a given position and direction.

        This method performs several checks before placing the domino:
        1.  Validates that the starting and ending positions are within the board boundaries.
        2.  Ensures that both cells the domino would occupy are currently empty.
        3.  Verifies that the given domino is a possible candidate for both cells
            (or its reversed version is).
        4.  After placing the domino, it checks if the new board state violates any
            partial constraints.

        If any check fails, the board is reverted to its state before the attempt,
        and the method returns False.

        Args:
            domino: The domino to be placed.
            position: The (row, col) tuple for the 'left' side of the domino.
            direction: The direction to place the 'right' side of the domino.

        Returns:
            True if the domino was placed successfully, False otherwise.
        """
        row1, col1 = position.row, position.col
        if not (0 <= row1 < self.n_row and 0 <= col1 < self.n_col):
            logging.debug(f"Start position {position} is out of bounds")
            return False

        saved_board = copy.deepcopy(self.board)

        if self.board[row1][col1] is not None:
            logging.debug(f"Position {position} is already occupied")
            return False

        if (
            domino not in self.possible_dominoes[row1][col1]
            and reverse_domino(domino) not in self.possible_dominoes[row1][col1]
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
            and reverse_domino(domino) not in self.possible_dominoes[row2][col2]
        ):
            logging.debug(f"Domino {domino} is not possible at {(row2, col2)}")
            return False

        self.board[row1][col1] = domino.left
        self.board[row2][col2] = domino.right

        if not self.check_partial_constraints():
            logging.debug(
                f"Domino {domino} violates partial constraints at {position} {direction}"
            )
            self.board = saved_board
            return False

        logging.debug(f"Domino {domino} placed at {position} {direction}")
        return True

    def sort_positions(self):
        self.sorted_positions = [
            Position(row=i, col=j) for i in range(self.n_row) for j in range(self.n_col)
        ]
        self.sorted_positions.sort(
            key=lambda x: (len(self.possible_dominoes[x.row][x.col]), x.row, x.col)
        )

    def find_next_empty_cell(self) -> Position | None:
        # first if there are cells that are of ConstraitType total and only one position and not occupied, select it
        for position in self.sorted_positions:
            if self.cell(position.row, position.col) is None:
                return position
        return None

    def _check_constraint(self, constraint: Constraint, is_partial: bool) -> bool:
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
                for position in constraint.positions:
                    cell_value = self.board[position.row][position.col]
                    if cell_value is not None:
                        if value is None:
                            value = cell_value
                        elif cell_value != value:
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
                is_complete = True
                for position in constraint.positions:
                    value = self.board[position.row][position.col]
                    if value is not None:
                        total += value
                    else:
                        is_complete = False
                if is_complete and total <= constraint.value:
                    return False

            case _:
                raise ValueError(
                    f"Unknown constraint type: {constraint.constraint_type}"
                )

        return True

    def check_constraints(self):
        self.print_board()
        for constraint in self.constraint_list:
            if not self._check_constraint(constraint, is_partial=False):
                return False
        return True

    def check_partial_constraints(self):
        for constraint in self.constraint_list:
            if not self._check_constraint(constraint, is_partial=True):
                return False
        return True

    def __repr__(self):
        result = ""
        for row in self.board:
            result += (
                "|"
                + "|".join(
                    [
                        "  "
                        if cell == -1
                        else f"{cell:>2}"
                        if cell is not None
                        else " ."
                        for cell in row
                    ]
                )
                + "|\n"
            )
        return result

    def print_possible_dominoes(self):
        for i, row in enumerate(self.possible_dominoes):
            for j, col in enumerate(row):
                print(f"{i},{j}: {col}")

    def print_constraints(self):
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
        print(self.__repr__())
