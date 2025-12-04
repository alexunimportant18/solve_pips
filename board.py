import copy
from constraint import Constraint, ConstraintType
from domino import Domino, value_distribution
from direction import Direction
import logging

def find_combinations(n: int, t: int) -> list[list[int]]:
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
    def find_combinations_recursive(n_rem: int, t_rem: int, current_combination: list[int]):
        if n_rem == 0:
            if t_rem == 0:
                result.append(current_combination)
            return

        # Optimization: Prune branches that can't possibly reach the target sum.
        if t_rem < 0 or n_rem * 6 < t_rem:
            return

        start = current_combination[-1] if current_combination else 0
        for i in range(start, 7):
            find_combinations_recursive(n_rem - 1, t_rem - i, current_combination + [i])

    result: list[list[int]] = []
    find_combinations_recursive(n, t, [])
    return result

def find_possible_dominoes_in_combination(combination: list[int], dominoes: set[Domino]) -> set[Domino]:
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
        if domino.left == value or domino.right == value:
            possible_dominoes.add(domino)
            temp.remove(domino)
            if len(temp) > 0:
                possible_dominoes.update(find_possible_dominoes_in_combination(combination[1:], temp))
                
    return possible_dominoes

def find_possible_dominoes_with_total_count(dominoes: set[Domino], count: int, value: int) -> set[Domino]:
    result: set[Domino] = set()
    combinations: list[list[int]] = find_combinations(count, value)

    for combination in combinations:
        result.update(find_possible_dominoes_in_combination(combination, dominoes))

    return result

def find_possible_dominoes_with_less_than(dominoes: set[Domino], count: int, value: int) -> set[Domino]:
    result: set[Domino] = set()
    for i in range(0, value):
        combinations: list[list[int]] = find_combinations(count, i)

        for combination in combinations:
            result.update(find_possible_dominoes_in_combination(combination, dominoes))

    logging.debug(f"find_possible_dominoes_with_less_than({dominoes}, {count}, {value}) = {result}")
    return result

def find_possible_dominoes_with_greater_than(dominoes: set[Domino], count: int, value: int) -> set[Domino]:
    result: set[Domino] = set()
    upperbound: int = count * 6 + 1
    for i in range(value + 1, upperbound):
        combinations: list[list[int]] = find_combinations(count, i)

        for combination in combinations:
            result.update(find_possible_dominoes_in_combination(combination, dominoes))

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
        self.board = [[None for _ in range(self.n_col)] for _ in range(self.n_row)]
        self.constraints = [[(ConstraintType.FREE, None) for _ in range(self.n_col)] for _ in range(self.n_row)]
        self.possible_dominoes = [[set() for _ in range(self.n_col)] for _ in range(self.n_row)]
        self.sorted_positions = []

    def add_constraint(self, constraint: Constraint) -> None:
        for position in constraint.positions:
            if self.board[position[0]][position[1]] is not None:
                raise ValueError(f"Position {position} is already occupied")

        match constraint.constraint_type:
            case ConstraintType.DEAD:
                for position in constraint.positions:
                    self.board[position[0]][position[1]] = -1
                    self.constraints[position[0]][position[1]] = (ConstraintType.DEAD, -1)

            case ConstraintType.EQUAL | ConstraintType.NE | ConstraintType.TOTAL | ConstraintType.LT | ConstraintType.GT:
                for position in constraint.positions:
                    self.constraints[position[0]][position[1]] = (constraint.constraint_type, constraint.value)

            case ConstraintType.FREE:
                for position in constraint.positions:
                    self.constraints[position[0]][position[1]] = (ConstraintType.FREE, None)

        self.constraint_list.append(constraint)

    def cell(self, row: int, col: int) -> int | None:
        return self.board[row][col]

    def generate_possible_dominoes(self, dominoes: set[Domino]):
        distribution: dict[int, int] = value_distribution(list(dominoes))
        logging.debug(f"{distribution=}")
        
        for constraint in self.constraint_list:
            match constraint.constraint_type:
                case ConstraintType.FREE | ConstraintType.NE:
                    for position in constraint.positions:
                        self.possible_dominoes[position[0]][position[1]] = set(dominoes)

                case ConstraintType.EQUAL:
                    minimum_count = len(constraint.positions)
                    # find all values that has at least the minimum count
                    result = set()
                    for i in range(0, 7):
                        if i in distribution.keys():
                            if distribution[i] >= minimum_count:
                                for domino in dominoes:
                                    if domino.left == i or domino.right == i:
                                        result.add(domino)

                    for position in constraint.positions:
                        self.possible_dominoes[position[0]][position[1]] = result

                case ConstraintType.TOTAL:
                    count = len(constraint.positions)
                    value = constraint.value
                    result = find_possible_dominoes_with_total_count(dominoes, count, value)
                    for position in constraint.positions:
                        self.possible_dominoes[position[0]][position[1]] = result                    

                case ConstraintType.LT:
                    count: int = len(constraint.positions)
                    value: int | None = constraint.value
                    result: set[Domino] = find_possible_dominoes_with_less_than(dominoes, count, value)
                    for position in constraint.positions:
                        self.possible_dominoes[position[0]][position[1]] = result   

                case ConstraintType.GT:
                    count: int = len(constraint.positions)
                    value: int | None = constraint.value
                    result: set[Domino] = find_possible_dominoes_with_greater_than(dominoes, count, value)
                    for position in constraint.positions:
                        self.possible_dominoes[position[0]][position[1]] = result   

                case ConstraintType.DEAD:
                    for position in constraint.positions:
                        self.possible_dominoes[position[0]][position[1]] = set()
        self.sort_positions()
        starts_from = 0
        for i, position in enumerate(self.sorted_positions):
            if self.cell(position[0], position[1]) is None:
                starts_from = i
                break
        self.sorted_positions = self.sorted_positions[starts_from:]

    def place_domino(self, domino: Domino, position: tuple[int, int], direction: Direction) -> bool:
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
        row1, col1 = position
        if not (0 <= row1 < self.n_row and 0 <= col1 < self.n_col):
            logging.debug(f"Start position {position} is out of bounds")
            return False

        saved_board = copy.deepcopy(self.board)

        if self.board[row1][col1] is not None:
            logging.debug(f"Position {position} is already occupied")
            return False

        #if domino not in self.possible_dominoes[row1][col1] and domino.reversed() not in self.possible_dominoes[row1][col1]:
        if domino not in self.possible_dominoes[row1][col1]:
            logging.debug(f"Domino {domino} is not possible at {position}")
            return False

        row2, col2 = position
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

        #if domino not in self.possible_dominoes[row2][col2] and domino.reversed() not in self.possible_dominoes[row2][col2]:
        if domino not in self.possible_dominoes[row2][col2]:
            logging.debug(f"Domino {domino} is not possible at {(row2, col2)}")
            return False
        
        self.board[row1][col1] = domino.left
        self.board[row2][col2] = domino.right

        if not self.check_partial_constraints():
            logging.debug(f"Domino {domino} violates partial constraints at {position} {direction}")
            self.board = saved_board
            return False

        logging.debug(f"Domino {domino} placed at {position} {direction}")
        return True

    def sort_positions(self):
        self.sorted_positions = [(i, j) for i in range(self.n_row) for j in range(self.n_col)]
        self.sorted_positions.sort(key=lambda x: (len(self.possible_dominoes[x[0]][x[1]]), x[0], x[1]))

    def find_next_empty_cell(self) -> tuple[int, int] | None:
        # first if there are cells that are of ConstraitType total and only one position and not occupied, select it
        for position in self.sorted_positions:
            if self.cell(position[0], position[1]) is None:
                return position
        return None


    def _check_constraint(self, constraint: Constraint, is_partial: bool) -> bool:
        match constraint.constraint_type:
            case ConstraintType.FREE:
                return True

            case ConstraintType.DEAD:
                for position in constraint.positions:
                    if self.board[position[0]][position[1]] != -1:
                        return False

            case ConstraintType.EQUAL:
                value = None
                for position in constraint.positions:
                    cell_value = self.board[position[0]][position[1]]
                    if cell_value is not None:
                        if value is None:
                            value = cell_value
                        elif cell_value != value:
                            return False

            case ConstraintType.NE:
                value_set = set()
                for position in constraint.positions:
                    cell_value = self.board[position[0]][position[1]]
                    if cell_value is not None:
                        if cell_value in value_set:
                            return False
                        value_set.add(cell_value)

            case ConstraintType.TOTAL:
                total = 0
                is_complete = True
                for position in constraint.positions:
                    value = self.board[position[0]][position[1]]
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
                total = 0
                for position in constraint.positions:
                    value = self.board[position[0]][position[1]]
                    if value is not None:
                        total += value
                if total >= constraint.value:
                    return False

            case ConstraintType.GT:
                total = 0
                is_complete = True
                for position in constraint.positions:
                    value = self.board[position[0]][position[1]]
                    if value is not None:
                        total += value
                    else:
                        is_complete = False
                if is_complete and total <= constraint.value:
                    return False

            case _:
                raise ValueError(f"Unknown constraint type: {constraint.constraint_type}")

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
            result += "|" + "|".join(['  ' if cell == -1 else f'{cell:>2}' if cell is not None else ' .' for cell in row]) + "|\n"
        return result


    def print_possible_dominoes(self):
        for i, row in enumerate(self.possible_dominoes):
            for j, col in enumerate(row):
                print(f"{i},{j}: {col}")
    def print_constraints(self):
        board_constraints = [[' .' for _ in range(self.n_col)] for _ in range(self.n_row)]
        for constraint in self.constraint_list:
            match constraint.constraint_type:
                case ConstraintType.FREE:
                    continue

                case ConstraintType.DEAD:
                    for position in constraint.positions:
                        board_constraints[position[0]][position[1]] = ' X'

                case ConstraintType.EQUAL:
                    for position in constraint.positions:
                        board_constraints[position[0]][position[1]] = ' ='

                case ConstraintType.LT:
                    for position in constraint.positions:
                        board_constraints[position[0]][position[1]] = f"<{constraint.value:1}"

                case ConstraintType.GT:
                    for position in constraint.positions:
                        board_constraints[position[0]][position[1]] = f">{constraint.value:1}"

                case ConstraintType.TOTAL:
                    for position in constraint.positions:
                        board_constraints[position[0]][position[1]] = f"{constraint.value:>2}"

        for row in board_constraints:
            print("|"+"|".join(row)+"|")

    def print_board(self):
        print(self.__repr__())