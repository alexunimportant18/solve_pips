import pytest
from board import Board, find_possible_dominoes_with_total_count, find_possible_dominoes_with_less_than, find_possible_dominoes_with_greater_than
from domino import Domino
from constraint import Constraint, ConstraintType
from direction import Direction

@pytest.fixture
def empty_board():
    return Board(2, 2)

@pytest.fixture
def sample_dominoes():
    return {
        Domino(1, 2), Domino(2, 3), Domino(3, 4), Domino(4, 5), Domino(5, 6), Domino(6, 1)
    }

def test_add_constraint_dead(empty_board):
    constraint = Constraint(ConstraintType.DEAD, [(0, 0)])
    empty_board.add_constraint(constraint)
    assert empty_board.cell(0, 0) == -1
    assert empty_board.constraints[0][0] == (ConstraintType.DEAD, -1)

def test_add_constraint_less_than(empty_board):
    constraint = Constraint(ConstraintType.LT, [(0, 0), (0, 1)], 3)
    empty_board.add_constraint(constraint)
    assert empty_board.state[0][0] == (ConstraintType.LT, 3)
    assert empty_board.state[0][1] == (ConstraintType.LT, 3)

def test_add_constraint_greater_than(empty_board):
    constraint = Constraint(ConstraintType.GT, [(0, 0), (0, 1)], 3)
    empty_board.add_constraint(constraint)
    assert empty_board.state[0][0] == (ConstraintType.GT, 3)
    assert empty_board.state[0][1] == (ConstraintType.GT, 3)

def test_add_constraint_not_equal(empty_board):
    constraint = Constraint(ConstraintType.NE, [(0, 0), (0, 1)], 5)
    empty_board.add_constraint(constraint)
    assert empty_board.state[0][0] == (ConstraintType.NE, 5)
    assert empty_board.state[0][1] == (ConstraintType.NE, 5)

def test_add_constraint_equal(empty_board):
    constraint = Constraint(ConstraintType.EQUAL, [(0, 0), (0, 1)], 5)
    empty_board.add_constraint(constraint)
    assert empty_board.state[0][0] == (ConstraintType.EQUAL, 5)
    assert empty_board.state[0][1] == (ConstraintType.EQUAL, 5)

def test_add_constraint_total(empty_board):
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (0, 1)], 5)
    empty_board.add_constraint(constraint)
    assert empty_board.state[0][0] == (ConstraintType.TOTAL, 5)
    assert empty_board.state[0][1] == (ConstraintType.TOTAL, 5)

def test_add_constraint_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(ConstraintType.DEAD, [(0, 0)])
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_lt_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(ConstraintType.LT, [(0, 0), (0, 1)], 3)
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_gt_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(ConstraintType.GT, [(0, 0), (0, 1)], 3)
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_ne_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(ConstraintType.NE, [(0, 0), (0, 1)], 5)
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_equal_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(ConstraintType.EQUAL, [(0, 0), (0, 1)], 5)
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_total_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (0, 1)], 5)
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_free_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(ConstraintType.FREE, [(0, 0)])
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)

# sample_dominoes = [Domino(1, 2), Domino(2, 3), Domino(3, 4), Domino(4, 5), Domino(5, 6), Domino(6, 1)]
def test_find_possible_dominoes_with_total_count(sample_dominoes):
    # Test case 1: Find dominoes for a total count of 3 with 2 dominoes
    # Possible combinations: (1, 2)
    result = find_possible_dominoes_with_total_count(sample_dominoes, count=2, value=3)
    assert result == {Domino(1, 2), Domino(2, 3), Domino(6, 1)}

    # Test case 2: No dominoes match the total count
    result = find_possible_dominoes_with_total_count(sample_dominoes, count=2, value=10)
    assert result == {Domino(3, 4), Domino(4, 5), Domino(5, 6), Domino(6, 1)}

    # Test case 3: All dominoes match
    result = find_possible_dominoes_with_total_count({Domino(1,1)}, count=1, value=1)
    assert result == {Domino(1, 1)}

# sample_dominoes is { Domino(1, 2), Domino(2, 3), Domino(3, 4), Domino(4, 5), Domino(5, 6), Domino(6, 1) }
def test_find_possible_dominoes_with_less_than(sample_dominoes):
    # Test case 1: Find dominoes with a total count less than 4
    result = find_possible_dominoes_with_less_than(sample_dominoes, count=2, value=4)
    assert result == {Domino(1, 2), Domino(2, 3), Domino(6, 1)}

    # Test case 2: No dominoes are less than the target
    result = find_possible_dominoes_with_less_than(sample_dominoes, count=2, value=2)
    assert len(result) == 0

    result = find_possible_dominoes_with_less_than(sample_dominoes, count=2, value=3)
    assert result == {Domino(1, 2), Domino(6, 1)}

    # Test case 3: All dominoes are less than the target
    result = find_possible_dominoes_with_less_than(sample_dominoes, count=2, value=12)
    assert result == sample_dominoes

# sample_dominoes is { Domino(1, 2), Domino(2, 3), Domino(3, 4), Domino(4, 5), Domino(5, 6), Domino(6, 1) }
def test_find_possible_dominoes_with_greater_than(sample_dominoes):
    # Test case 1: Find dominoes with a total count greater than 10
    result = find_possible_dominoes_with_greater_than(sample_dominoes, count=2, value=10)
    assert result == {Domino(4, 5), Domino(5, 6), Domino(6, 1)}

    # Test case 2: No dominoes are greater than the target
    result = find_possible_dominoes_with_greater_than(sample_dominoes, count=2, value=11)
    assert result == {Domino(5, 6), Domino(6, 1)}

    # Test case 3: All dominoes are greater than the target
    result = find_possible_dominoes_with_greater_than(sample_dominoes, 2, 2)
    assert result == sample_dominoes

def test_generate_possible_dominoes_total_constraint():
    board = Board(2, 2)
    dominoes = {Domino(1, 2), Domino(3, 4), Domino(5, 6)}
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (0, 1)], 3)
    board.add_constraint(constraint)
    board.generate_possible_dominoes(dominoes)
    expected_dominoes = {Domino(1, 2)}
    assert board.possible_dominoes[0][0] == expected_dominoes
    assert board.possible_dominoes[0][1] == expected_dominoes

def test_generate_possible_dominoes_equal_constraint():
    board = Board(2, 2)
    dominoes = {Domino(1, 1), Domino(1, 2), Domino(2, 2)}
    constraint = Constraint(ConstraintType.EQUAL, [(0, 0), (0, 1)])
    board.add_constraint(constraint)
    board.generate_possible_dominoes(dominoes)
    expected_dominoes = {Domino(1, 1), Domino(1, 2), Domino(2, 2)}
    assert board.possible_dominoes[0][0] == expected_dominoes
    assert board.possible_dominoes[0][1] == expected_dominoes

def test_generate_possible_dominoes_dead_constraint():
    board = Board(2, 2)
    dominoes = {Domino(1, 2), Domino(3, 4)}
    constraint = Constraint(ConstraintType.DEAD, [(0, 0)])
    board.add_constraint(constraint)
    board.generate_possible_dominoes(dominoes)
    assert board.possible_dominoes[0][0] == set()

def test_generate_possible_dominoes_free_and_ne_constraints():
    board = Board(2, 2)
    dominoes = {Domino(1, 2), Domino(3, 4)}
    free_constraint = Constraint(ConstraintType.FREE, [(0, 0)])
    ne_constraint = Constraint(ConstraintType.NE, [(0, 1)])
    board.add_constraint(free_constraint)
    board.add_constraint(ne_constraint)
    board.generate_possible_dominoes(dominoes)
    assert board.possible_dominoes[0][0] == dominoes
    assert board.possible_dominoes[0][1] == dominoes

def test_generate_possible_dominoes_lt_constraint():
    board = Board(2, 2)
    dominoes = {Domino(1, 2), Domino(3, 4), Domino(5, 6)}
    constraint = Constraint(ConstraintType.LT, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.generate_possible_dominoes(dominoes)
    expected_dominoes = {Domino(1, 2), Domino(3, 4)}
    assert board.possible_dominoes[0][0] == expected_dominoes
    assert board.possible_dominoes[0][1] == expected_dominoes

def test_generate_possible_dominoes_gt_constraint():
    board = Board(2, 2)
    dominoes = {Domino(1, 2), Domino(3, 4), Domino(5, 6)}
    constraint = Constraint(ConstraintType.GT, [(0, 0), (0, 1)], 8)
    board.add_constraint(constraint)
    board.generate_possible_dominoes(dominoes)
    expected_dominoes = {Domino(3, 4), Domino(5, 6)}
    assert board.possible_dominoes[0][0] == expected_dominoes
    assert board.possible_dominoes[0][1] == expected_dominoes

def test_check_constraints_total_pass():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.board[0][0] = 2
    board.board[0][1] = 3
    assert board.check_constraints() is True

def test_check_constraints_total_fail():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.board[0][0] = 3
    board.board[0][1] = 3
    assert board.check_constraints() is False

def test_check_partial_constraints_total_pass():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.board[0][0] = 2
    assert board.check_partial_constraints() is True

def test_check_partial_constraints_total_fail():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.board[0][0] = 6
    assert board.check_partial_constraints() is False

def test_check_partial_constraints_equal_pass():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.EQUAL, [(0, 0), (0, 1)])
    board.add_constraint(constraint)
    board.board[0][0] = 2
    assert board.check_partial_constraints() is True

def test_check_partial_constraints_equal_fail():
    board = Board(2, 2)
    constraint = Constraint(ConstraintType.EQUAL, [(0, 0), (0, 1), (1,0)])
    board.add_constraint(constraint)
    board.board[0][0] = 2
    board.board[0][1] = 3
    assert board.check_partial_constraints() is False

def test_check_partial_constraints_ne_pass():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.NE, [(0, 0), (0, 1)])
    board.add_constraint(constraint)
    board.board[0][0] = 2
    assert board.check_partial_constraints() is True

def test_check_partial_constraints_ne_fail():
    board = Board(2, 2)
    constraint = Constraint(ConstraintType.NE, [(0, 0), (0, 1)])
    board.add_constraint(constraint)
    board.board[0][0] = 2
    board.board[0][1] = 2
    assert board.check_partial_constraints() is False

def test_check_partial_constraints_lt_pass():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.LT, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.board[0][0] = 1
    assert board.check_partial_constraints() is True

def test_check_partial_constraints_lt_fail():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.LT, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.board[0][0] = 5
    assert board.check_partial_constraints() is False

def test_check_partial_constraints_gt_pass():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.GT, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.board[0][0] = 4
    board.board[0][1] = 3
    assert board.check_partial_constraints() is True

def test_check_partial_constraints_gt_fail():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.GT, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.board[0][0] = 2
    board.board[0][1] = 3
    assert board.check_partial_constraints() is False

def test_check_partial_constraints_dead_pass():
    board = Board(1, 1)
    constraint = Constraint(ConstraintType.DEAD, [(0, 0)])
    board.add_constraint(constraint)
    assert board.check_partial_constraints() is True

def test_check_partial_constraints_dead_fail():
    board = Board(1, 1)
    constraint = Constraint(ConstraintType.DEAD, [(0, 0)])
    board.add_constraint(constraint)
    board.board[0][0] = 1
    assert board.check_partial_constraints() is False

def test_check_constraints_free_pass():
    board = Board(1, 1)
    constraint = Constraint(ConstraintType.FREE, [(0, 0)])
    board.add_constraint(constraint)
    board.board[0][0] = 1
    assert board.check_constraints() is True

def test_check_constraints_ne_pass_with_none():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.NE, [(0, 0), (0, 1)])
    board.add_constraint(constraint)
    board.board[0][0] = 2
    assert board.check_constraints() is True

def test_check_constraints_unknown_type():
    board = Board(1, 1)
    constraint = Constraint("UNKNOWN", [(0, 0)])
    board.add_constraint(constraint)
    with pytest.raises(ValueError):
        board.check_constraints()

def test_check_constraints_dead_fail_with_value():
    board = Board(1, 1)
    constraint = Constraint(ConstraintType.DEAD, [(0, 0)])
    board.add_constraint(constraint)
    board.board[0][0] = 0
    assert board.check_constraints() is False

def test_check_constraints_equal_pass_with_none():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.EQUAL, [(0, 0), (0, 1)])
    board.add_constraint(constraint)
    board.board[0][0] = None
    assert board.check_constraints() is True

def test_check_constraints_gt_fail_with_none():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.GT, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.board[0][0] = 6
    board.board[0][1] = None
    assert board.check_constraints() is True

def test_check_constraints_lt_fail_with_none():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.LT, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.board[0][0] = 4
    board.board[0][1] = None
    assert board.check_constraints() is True

def test_place_domino_occupied_cell():
    board = Board(2, 2)
    board.board[0][0] = 1
    domino = Domino(2, 3)
    assert board.place_domino(domino, (0, 0), Direction.EAST) is False

def test_place_domino_not_possible():
    board = Board(2, 2)
    board.possible_dominoes[0][0] = {Domino(1, 1)}
    domino = Domino(2, 3)
    assert board.place_domino(domino, (0, 0), Direction.EAST) is False

def test_place_domino_not_possible_in_second_cell():
    board = Board(width=2, height=2)
    domino = Domino(1, 2)
    board.possible_dominoes[0][0] = {domino}
    board.possible_dominoes[0][1] = {Domino(3, 4)}
    assert board.place_domino(domino, (0, 0), Direction.EAST) is False
    assert board.place_domino(domino, (0, 0), Direction.WEST) is False

def test_place_domino_violates_partial_constraints_after_placement():
    board = Board(1, 2)
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (1, 0)], 3)
    board.add_constraint(constraint)
    domino = Domino(4, 1)
    board.possible_dominoes[0][0] = {domino}
    board.possible_dominoes[1][0] = {domino}
    assert board.place_domino(domino, (0, 0), Direction.SOUTH) is False

def test_place_domino_out_of_bounds():
    board = Board(2, 2)
    board.possible_dominoes[0][0] = {Domino(1, 2)}
    board.possible_dominoes[0][1] = {Domino(1, 2)}
    domino = Domino(1, 2)
    assert board.place_domino(domino, (0, 0), Direction.NORTH) is False
    assert board.place_domino(domino, (0, 1), Direction.EAST) is False
    assert board.place_domino(domino, (1, 1), Direction.SOUTH) is False
    assert board.place_domino(domino, (1, 0), Direction.WEST) is False

def test_place_domino_adjacent_cell_occupied():
    board = Board(2, 2)
    board.possible_dominoes[0][0] = {Domino(1, 2)}
    board.possible_dominoes[0][1] = {Domino(1, 2)}
    board.board[0][1] = 3
    domino = Domino(1, 2)
    assert board.place_domino(domino, (0, 0), Direction.EAST) is False

def test_place_domino_violates_partial_constraints():
    board = Board(2, 1)
    constraint = Constraint(ConstraintType.TOTAL, [(0, 0), (0, 1)], 5)
    board.add_constraint(constraint)
    board.possible_dominoes[0][0] = {Domino(6, 1)}
    board.possible_dominoes[0][1] = {Domino(6, 1)}
    domino = Domino(6, 1)
    assert board.place_domino(domino, (0, 0), Direction.SOUTH) is False

def test_place_domino_success():
    board = Board(1, 2)
    board.possible_dominoes[0][0] = {Domino(1, 2)}
    board.possible_dominoes[1][0] = {Domino(1, 2)}
    domino = Domino(1, 2)
    assert board.place_domino(domino, (0, 0), Direction.SOUTH) is True
    assert board.board[0][0] == 1
    assert board.board[1][0] == 2

def test_print_possible_dominoes(capsys):
    board = Board(width=2, height=1)
    domino_set = {Domino(1, 2), Domino(3, 4)}
    board.possible_dominoes[0][0] = domino_set
    board.possible_dominoes[0][1] = {Domino(5, 6)}
    board.print_possible_dominoes()
    captured = capsys.readouterr()
    
    # The order of dominoes in the set can vary, so we check for substrings
    assert "0,0:" in captured.out
    assert str(domino_set) in captured.out
    assert f"0,1: {{{Domino(5, 6)}}}\n" in captured.out

def test_print_constraints(capsys):
    board = Board(width=3, height=2)
    board.add_constraint(Constraint(ConstraintType.DEAD, [(0, 0)]))
    board.add_constraint(Constraint(ConstraintType.EQUAL, [(0, 1)]))
    board.add_constraint(Constraint(ConstraintType.LT, [(0, 2)], 4))
    board.add_constraint(Constraint(ConstraintType.GT, [(1, 0)], 5))
    board.add_constraint(Constraint(ConstraintType.TOTAL, [(1, 1)], 10))
    board.add_constraint(Constraint(ConstraintType.FREE, [(1, 2)]))
    
    board.print_constraints()
    captured = capsys.readouterr()
    
    expected_output = (
        "| X| =|<4|\n"
        "|>5|10| .|\n"
    )
    assert captured.out == expected_output


def test_find_next_empty_cell_all_filled():
    board = Board(2, 2)
    board.board = [[1, 2], [3, 4]]
    board.sort_positions()
    assert board.find_next_empty_cell() is None

def test_find_next_empty_cell_one_empty():
    board = Board(2, 2)
    board.board = [[1, 2], [3, None]]
    board.sort_positions()
    assert board.find_next_empty_cell() == (1, 1)

def test_find_next_empty_cell_sorted_by_possibilities():
    board = Board(2, 2)
    board.possible_dominoes[0][0] = {Domino(1, 2), Domino(3, 4)}
    board.possible_dominoes[0][1] = {Domino(1, 2)}
    board.possible_dominoes[1][0] = {Domino(1, 2), Domino(3, 4), Domino(5, 6)}
    board.possible_dominoes[1][1] = {Domino(1, 2), Domino(3, 4)}
    board.sort_positions()
    assert board.find_next_empty_cell() == (0, 1)