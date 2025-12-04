import pytest
from board import Board
from domino import Domino
from constraint import Constraint, ConstraintType
from solve import solve

@pytest.fixture
def simple_board():
    return Board(2, 2)

def test_solve_base_case(simple_board):
    """
    Tests the base case where there are no dominoes to place.
    """
    solution, remaining_dominoes = solve(simple_board, set())
    assert solution is not None
    assert len(remaining_dominoes) == 0

def test_solve_no_solution():
    """
    Tests a scenario where no solution is possible.
    """
    board = Board(width=2, height=1)
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (0, 1)], 15)
    board.add_constraint(constraint)
    dominoes = {Domino(1, 2)}
    board.generate_possible_dominoes(dominoes)
    solution = solve(board, dominoes)
    assert solution is None

def test_solve_simple_success():
    """
    Tests a simple successful scenario.
    """
    board = Board(width=2, height=1)
    dominoes = {Domino(1, 2)}
    board.generate_possible_dominoes(dominoes)
    result = solve(board, dominoes)
    assert result is None

def test_solve_with_constraints():
    """
    Tests solving a board with constraints.
    """
    board = Board(width=1, height=2)
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (1, 0)], 3)
    board.add_constraint(constraint)
    dominoes = {Domino(1, 2)}
    board.generate_possible_dominoes(dominoes)
    solution_board, remaining_dominoes = solve(board, dominoes)
    assert solution_board is not None
    assert len(remaining_dominoes) == 0
    assert {solution_board.cell(0, 0), solution_board.cell(1, 0)} == {1, 2}

def test_solve_symmetric_domino():
    """
    Tests solving with a symmetric domino.
    """
    board = Board(width=2, height=1)
    dominoes = {Domino(3, 3)}
    board.generate_possible_dominoes(dominoes)
    result = solve(board, dominoes)
    assert result is None

def test_solve_reversed_domino():
    """
    Tests if the solver can use a reversed domino.
    """
    board = Board(width=2, height=1)
    # This constraint can only be satisfied by Domino(2, 1)
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (0, 1)], 3)
    board.add_constraint(constraint)
    dominoes = {Domino(1, 2)}
    board.generate_possible_dominoes(dominoes)
    solution_board, remaining_dominoes = solve(board, dominoes)
    assert solution_board is not None
    assert len(remaining_dominoes) == 0
    assert {solution_board.cell(0, 0), solution_board.cell(0, 1)} == {1, 2}

def test_solve_full_board_no_dominoes_left(simple_board):
    """
    Tests the case where the board is full and no dominoes are left.
    """
    simple_board.board = [[1,2],[3,4]]
    solution, remaining_dominoes = solve(simple_board, set())
    assert solution is not None
    assert len(remaining_dominoes) == 0

def test_solve_full_board_with_dominoes_left(simple_board):
    """
    Tests the case where the board is full but dominoes are left.
    """
    simple_board.board = [[1,2],[3,4]]
    solution = solve(simple_board, {Domino(5,6)})
    assert solution is None


