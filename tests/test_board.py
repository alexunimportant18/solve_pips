import pytest

from board import (
    Board,
    find_possible_dominoes_with_greater_than,
    find_possible_dominoes_with_less_than,
    find_possible_dominoes_with_total_count,
)
from constraint import Constraint, ConstraintType
from domino import Domino
from position import Position


@pytest.fixture
def empty_board():
    return Board(2, 2)


@pytest.fixture
def sample_dominoes():
    return {
        Domino(1, 2),
        Domino(2, 3),
        Domino(3, 4),
        Domino(4, 5),
        Domino(5, 6),
        Domino(6, 1),
    }


def test_add_constraint_dead(empty_board):
    constraint = Constraint(ConstraintType.DEAD, [Position(row=0, col=0)])
    empty_board.add_constraint(constraint)
    assert empty_board.cell(0, 0) == -1
    assert empty_board.constraints[0][0].constraint_type == ConstraintType.DEAD


def test_add_constraint_less_than(empty_board):
    constraint = Constraint(
        ConstraintType.LT, [Position(row=0, col=0), Position(row=0, col=1)], 3
    )
    empty_board.add_constraint(constraint)
    assert empty_board.constraints[0][0].constraint_type == ConstraintType.LT
    assert empty_board.constraints[0][1].constraint_type == ConstraintType.LT


def test_add_constraint_greater_than(empty_board):
    constraint = Constraint(
        ConstraintType.GT, [Position(row=0, col=0), Position(row=0, col=1)], 3
    )
    empty_board.add_constraint(constraint)
    assert empty_board.constraints[0][0].constraint_type == ConstraintType.GT
    assert empty_board.constraints[0][1].constraint_type == ConstraintType.GT


def test_add_constraint_not_equal(empty_board):
    constraint = Constraint(
        ConstraintType.NE, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    empty_board.add_constraint(constraint)
    assert empty_board.constraints[0][0].constraint_type == ConstraintType.NE
    assert empty_board.constraints[0][1].constraint_type == ConstraintType.NE


def test_add_constraint_equal(empty_board):
    constraint = Constraint(
        ConstraintType.EQUAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    empty_board.add_constraint(constraint)
    assert empty_board.constraints[0][0].constraint_type == ConstraintType.EQUAL
    assert empty_board.constraints[0][1].constraint_type == ConstraintType.EQUAL


def test_add_constraint_total(empty_board):
    constraint = Constraint(
        ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    empty_board.add_constraint(constraint)
    assert empty_board.constraints[0][0].constraint_type == ConstraintType.TOTAL
    assert empty_board.constraints[0][1].constraint_type == ConstraintType.TOTAL


def test_add_constraint_value(empty_board):
    constraint = Constraint(ConstraintType.VALUE, [Position(row=0, col=0)], 3)
    empty_board.add_constraint(constraint)
    assert empty_board.constraints[0][0].constraint_type == ConstraintType.VALUE
    assert empty_board.constraints[0][0].value == 3


def test_add_constraint_value_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(ConstraintType.VALUE, [Position(row=0, col=0)], 3)
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(ConstraintType.DEAD, [Position(row=0, col=0)])
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_lt_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(
        ConstraintType.LT, [Position(row=0, col=0), Position(row=0, col=1)], 3
    )
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_gt_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(
        ConstraintType.GT, [Position(row=0, col=0), Position(row=0, col=1)], 3
    )
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_ne_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(
        ConstraintType.NE, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_equal_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(
        ConstraintType.EQUAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_total_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(
        ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_add_constraint_free_occupied_cell(empty_board):
    empty_board.board[0][0] = 1
    constraint = Constraint(ConstraintType.FREE, [Position(row=0, col=0)])
    with pytest.raises(ValueError):
        empty_board.add_constraint(constraint)


def test_find_possible_dominoes_with_total_count(sample_dominoes):
    result = find_possible_dominoes_with_total_count(sample_dominoes, count=2, value=3)
    assert result == {Domino(1, 2), Domino(2, 3), Domino(6, 1)}

    result = find_possible_dominoes_with_total_count(sample_dominoes, count=2, value=10)
    assert result == {Domino(3, 4), Domino(4, 5), Domino(5, 6), Domino(6, 1)}

    result = find_possible_dominoes_with_total_count({Domino(1, 1)}, count=1, value=1)
    assert result == {Domino(1, 1)}


def test_find_possible_dominoes_with_less_than(sample_dominoes):
    result = find_possible_dominoes_with_less_than(sample_dominoes, count=2, value=4)
    assert result == {Domino(1, 2), Domino(2, 3), Domino(6, 1)}

    result = find_possible_dominoes_with_less_than(sample_dominoes, count=2, value=2)
    assert len(result) == 0

    result = find_possible_dominoes_with_less_than(sample_dominoes, count=2, value=3)
    assert result == {Domino(1, 2), Domino(6, 1)}

    result = find_possible_dominoes_with_less_than(sample_dominoes, count=2, value=12)
    assert result == sample_dominoes


def test_find_possible_dominoes_with_greater_than(sample_dominoes):
    result = find_possible_dominoes_with_greater_than(
        sample_dominoes, count=2, value=10
    )
    assert result == {Domino(4, 5), Domino(5, 6), Domino(6, 1)}

    result = find_possible_dominoes_with_greater_than(
        sample_dominoes, count=2, value=11
    )
    assert result == {Domino(5, 6), Domino(6, 1)}

    result = find_possible_dominoes_with_greater_than(sample_dominoes, 2, 2)
    assert result == sample_dominoes


def test_generate_possible_dominoes_total_constraint():
    board = Board(2, 2)
    dominoes = {Domino(1, 2), Domino(3, 4), Domino(5, 6)}
    constraint = Constraint(
        ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 3
    )
    board.add_constraint(constraint)
    board.generate_possible_dominoes(dominoes)
    expected_dominoes = {Domino(1, 2)}
    assert board.possible_dominoes[0][0] == expected_dominoes
    assert board.possible_dominoes[0][1] == expected_dominoes


def test_generate_possible_dominoes_equal_constraint():
    board = Board(2, 2)
    dominoes = {Domino(1, 1), Domino(1, 2), Domino(2, 2)}
    constraint = Constraint(
        ConstraintType.EQUAL, [Position(row=0, col=0), Position(row=0, col=1)]
    )
    board.add_constraint(constraint)
    board.generate_possible_dominoes(dominoes)
    expected_dominoes = {Domino(1, 1), Domino(1, 2), Domino(2, 2)}
    assert board.possible_dominoes[0][0] == expected_dominoes
    assert board.possible_dominoes[0][1] == expected_dominoes


def test_generate_possible_dominoes_dead_constraint():
    board = Board(2, 2)
    dominoes = {Domino(1, 2), Domino(3, 4)}
    constraint = Constraint(ConstraintType.DEAD, [Position(row=0, col=0)])
    board.add_constraint(constraint)
    board.generate_possible_dominoes(dominoes)
    assert board.possible_dominoes[0][0] == set()


def test_generate_possible_dominoes_free_and_ne_constraints():
    board = Board(2, 2)
    dominoes = {Domino(1, 2), Domino(3, 4)}
    free_constraint = Constraint(ConstraintType.FREE, [Position(row=0, col=0)])
    ne_constraint = Constraint(ConstraintType.NE, [Position(row=0, col=1)])
    board.add_constraint(free_constraint)
    board.add_constraint(ne_constraint)
    board.generate_possible_dominoes(dominoes)
    assert board.possible_dominoes[0][0] == dominoes
    assert board.possible_dominoes[0][1] == dominoes


def test_generate_possible_dominoes_lt_constraint():
    board = Board(2, 2)
    dominoes = {Domino(1, 2), Domino(3, 4), Domino(5, 6)}
    constraint = Constraint(
        ConstraintType.LT, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    board.add_constraint(constraint)
    board.generate_possible_dominoes(dominoes)
    expected_dominoes = {Domino(1, 2), Domino(3, 4)}
    assert board.possible_dominoes[0][0] == expected_dominoes
    assert board.possible_dominoes[0][1] == expected_dominoes


def test_generate_possible_dominoes_gt_constraint():
    board = Board(2, 2)
    dominoes = {Domino(1, 2), Domino(3, 4), Domino(5, 6)}
    constraint = Constraint(
        ConstraintType.GT, [Position(row=0, col=0), Position(row=0, col=1)], 8
    )
    board.add_constraint(constraint)
    board.generate_possible_dominoes(dominoes)
    expected_dominoes = {Domino(3, 4), Domino(5, 6)}
    assert board.possible_dominoes[0][0] == expected_dominoes
    assert board.possible_dominoes[0][1] == expected_dominoes


def test_print_possible_dominoes(capsys):
    board = Board(width=2, height=1)
    domino_set = {Domino(1, 2), Domino(3, 4)}
    board.possible_dominoes[0][0] = domino_set
    board.possible_dominoes[0][1] = {Domino(5, 6)}
    board.print_possible_dominoes()
    captured = capsys.readouterr()

    assert "0,0:" in captured.out
    assert str(domino_set) in captured.out
    assert f"0,1: {{{Domino(5, 6)}}}\n" in captured.out


def test_print_constraints(capsys):
    board = Board(width=3, height=2)
    board.add_constraint(Constraint(ConstraintType.DEAD, [Position(row=0, col=0)]))
    board.add_constraint(Constraint(ConstraintType.EQUAL, [Position(row=0, col=1)]))
    board.add_constraint(Constraint(ConstraintType.LT, [Position(row=0, col=2)], 4))
    board.add_constraint(Constraint(ConstraintType.GT, [Position(row=1, col=0)], 5))
    board.add_constraint(Constraint(ConstraintType.TOTAL, [Position(row=1, col=1)], 10))
    board.add_constraint(Constraint(ConstraintType.FREE, [Position(row=1, col=2)]))

    board.print_constraints()
    captured = capsys.readouterr()

    expected_output = "| X | = |< 4|\n|> 5|+10| . |\n"
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
    assert board.find_next_empty_cell() == Position(row=1, col=1)


def test_find_next_empty_cell_sorted_by_possibilities():
    board = Board(2, 2)
    board.possible_dominoes[0][0] = {Domino(1, 2), Domino(3, 4)}
    board.possible_dominoes[0][1] = {Domino(1, 2)}
    board.possible_dominoes[1][0] = {Domino(1, 2), Domino(3, 4), Domino(5, 6)}
    board.possible_dominoes[1][1] = {Domino(1, 2), Domino(3, 4)}
    board.sort_positions()
    assert board.find_next_empty_cell() == Position(row=0, col=1)


def test_check_constraint_free():
    """Test that FREE constraint always returns True."""
    board = Board(2, 2)
    constraint = Constraint(ConstraintType.FREE, [Position(row=0, col=0)])
    assert board._check_constraint(constraint, [], is_partial=False) is True


def test_check_constraint_value_success():
    """Test that VALUE constraint passes when cell matches the required value."""
    board = Board(2, 2)
    board.board[0][0] = 3
    constraint = Constraint(ConstraintType.VALUE, [Position(row=0, col=0)], 3)
    assert board._check_constraint(constraint, [], is_partial=False) is True


def test_check_constraint_value_fail():
    """Test that VALUE constraint fails when cell doesn't match required value."""
    board = Board(2, 2)
    board.board[0][0] = 4
    constraint = Constraint(ConstraintType.VALUE, [Position(row=0, col=0)], 3)
    assert board._check_constraint(constraint, [], is_partial=False) is False


def test_check_constraint_value_none_value_error():
    """Test that VALUE constraint raises ValueError when no value is provided."""
    board = Board(2, 2)
    constraint = Constraint(ConstraintType.VALUE, [Position(row=0, col=0)], None)
    with pytest.raises(ValueError, match="value must be provided"):
        board._check_constraint(constraint, [], is_partial=False)


def test_check_constraint_dead_success():
    """Test that DEAD constraint passes when cell is correctly set to -1."""
    board = Board(2, 2)
    board.board[0][0] = -1
    constraint = Constraint(ConstraintType.DEAD, [Position(row=0, col=0)])
    assert board._check_constraint(constraint, [], is_partial=False) is True


def test_check_constraint_dead_fail():
    """Test that DEAD constraint fails when cell is not -1."""
    board = Board(2, 2)
    board.board[0][0] = 3
    constraint = Constraint(ConstraintType.DEAD, [Position(row=0, col=0)])
    assert board._check_constraint(constraint, [], is_partial=False) is False


def test_check_constraint_equal_success():
    """Test that EQUAL constraint passes when all cells have the same value."""
    board = Board(2, 2)
    board.board[0][0] = 3
    board.board[0][1] = 3
    constraint = Constraint(
        ConstraintType.EQUAL, [Position(row=0, col=0), Position(row=0, col=1)]
    )
    assert board._check_constraint(constraint, [], is_partial=False) is True


def test_check_constraint_equal_fail():
    """Test that EQUAL constraint fails when cells have different values."""
    board = Board(2, 2)
    board.board[0][0] = 3
    board.board[0][1] = 4
    constraint = Constraint(
        ConstraintType.EQUAL, [Position(row=0, col=0), Position(row=0, col=1)]
    )
    assert board._check_constraint(constraint, [], is_partial=False) is False


def test_check_constraint_ne_success():
    """Test that NE constraint passes when all cells have different values."""
    board = Board(2, 2)
    board.board[0][0] = 3
    board.board[0][1] = 4
    constraint = Constraint(
        ConstraintType.NE, [Position(row=0, col=0), Position(row=0, col=1)]
    )
    assert board._check_constraint(constraint, [], is_partial=False) is True


def test_check_constraint_ne_fail():
    """Test that NE constraint fails when cells have the same value."""
    board = Board(2, 2)
    board.board[0][0] = 3
    board.board[0][1] = 3
    constraint = Constraint(
        ConstraintType.NE, [Position(row=0, col=0), Position(row=0, col=1)]
    )
    assert board._check_constraint(constraint, [], is_partial=False) is False


def test_check_constraint_total_success_complete():
    """Test that TOTAL constraint passes when sum matches required value (board complete)."""
    board = Board(2, 2)
    board.board[0][0] = 2
    board.board[0][1] = 3
    constraint = Constraint(
        ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    assert board._check_constraint(constraint, [], is_partial=False) is True


def test_check_constraint_total_fail_wrong_sum():
    """Test that TOTAL constraint fails when sum doesn't match required value."""
    board = Board(2, 2)
    board.board[0][0] = 2
    board.board[0][1] = 4
    constraint = Constraint(
        ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    assert board._check_constraint(constraint, [], is_partial=False) is False


def test_check_constraint_total_none_value_error():
    """Test that TOTAL constraint raises ValueError when no value is provided."""
    board = Board(2, 2)
    constraint = Constraint(
        ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], None
    )
    with pytest.raises(ValueError, match="value must be provided"):
        board._check_constraint(constraint, [], is_partial=False)


def test_check_constraint_lt_success():
    """Test that LT constraint passes when sum is less than required value."""
    board = Board(2, 2)
    board.board[0][0] = 2
    board.board[0][1] = 2
    constraint = Constraint(
        ConstraintType.LT, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    assert board._check_constraint(constraint, [], is_partial=False) is True


def test_check_constraint_lt_fail():
    """Test that LT constraint fails when sum is >= required value."""
    board = Board(2, 2)
    board.board[0][0] = 3
    board.board[0][1] = 2
    constraint = Constraint(
        ConstraintType.LT, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    assert board._check_constraint(constraint, [], is_partial=False) is False


def test_check_constraint_lt_none_value_error():
    """Test that LT constraint raises ValueError when no value is provided."""
    board = Board(2, 2)
    constraint = Constraint(
        ConstraintType.LT, [Position(row=0, col=0), Position(row=0, col=1)], None
    )
    with pytest.raises(ValueError, match="value must be provided"):
        board._check_constraint(constraint, [], is_partial=False)


def test_check_constraint_gt_success_complete():
    """Test that GT constraint passes when sum is greater than required value (board complete)."""
    board = Board(2, 2)
    board.board[0][0] = 3
    board.board[0][1] = 3
    constraint = Constraint(
        ConstraintType.GT, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    assert board._check_constraint(constraint, [], is_partial=False) is True


def test_check_constraint_gt_fail():
    """Test that GT constraint fails when sum is <= required value."""
    board = Board(2, 2)
    board.board[0][0] = 2
    board.board[0][1] = 2
    constraint = Constraint(
        ConstraintType.GT, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    assert board._check_constraint(constraint, [], is_partial=False) is False


def test_check_constraint_gt_none_value_error():
    """Test that GT constraint raises ValueError when no value is provided."""
    board = Board(2, 2)
    constraint = Constraint(
        ConstraintType.GT, [Position(row=0, col=0), Position(row=0, col=1)], None
    )
    with pytest.raises(ValueError, match="value must be provided"):
        board._check_constraint(constraint, [], is_partial=False)


def test_check_constraint_unknown_type():
    """Test that unknown constraint type raises ValueError."""
    board = Board(1, 1)
    constraint = Constraint("UNKNOWN", [Position(row=0, col=0)])
    with pytest.raises(ValueError, match="Unknown constraint type:"):
        board._check_constraint(constraint, [], is_partial=False)


def test_check_partial_constraints_all_pass():
    """Test that check_partial_constraints returns True when all constraints are satisfied."""
    board = Board(2, 2)
    # Add valid constraints
    board.add_constraint(
        Constraint(
            ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
        )
    )
    board.add_constraint(Constraint(ConstraintType.FREE, [Position(row=1, col=0)]))
    # Place values that don't violate any constraints
    board.board[0][0] = 2
    board.board[0][1] = None
    # Available dominoes list (empty for this test)
    assert board.check_partial_constraints([]) is True


def test_check_partial_constraints_one_fails():
    """Test that check_partial_constraints returns False when any constraint is violated."""
    board = Board(2, 2)
    # Add constraints, one of which will be violated
    board.add_constraint(
        Constraint(
            ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
        )
    )
    board.add_constraint(
        Constraint(ConstraintType.NE, [Position(row=0, col=0), Position(row=0, col=1)])
    )
    # Place duplicate values that violate NE constraint
    board.board[0][0] = 3
    board.board[0][1] = 3
    # This should fail because NE constraint is violated
    assert board.check_partial_constraints([]) is False


def test_check_constraint_total_partial_success_incomplete():
    """Test that TOTAL constraint passes for partial board when sum is still possible."""
    board = Board(2, 2)
    board.board[0][0] = 2  # Only one cell filled
    constraint = Constraint(
        ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    # is_partial=True: sum is 2 < 5, which is still possible
    assert board._check_constraint(constraint, [], is_partial=True) is True


def test_check_constraint_total_partial_fail_exceeds_value():
    """Test that TOTAL constraint fails for partial board when sum already exceeds required value."""
    board = Board(2, 2)
    board.board[0][0] = 6  # Only one cell filled, but already over limit
    constraint = Constraint(
        ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    # is_partial=True: sum is 6 > 5, which is impossible
    assert board._check_constraint(constraint, [], is_partial=True) is False


def test_check_constraint_total_partial_fail_complete_wrong_sum():
    """Test that TOTAL constraint fails for partial board when board is complete but sum is wrong."""
    board = Board(2, 2)
    board.board[0][0] = 2
    board.board[0][1] = 4  # Sum is 6, but required is 5
    constraint = Constraint(
        ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    # is_partial=True: board is complete but sum is wrong
    assert board._check_constraint(constraint, [], is_partial=True) is False


def test_check_constraint_gt_partial_success_incomplete():
    """Test that GT constraint passes for partial board when max possible sum still exceeds required value."""
    board = Board(2, 2)
    board.board[0][0] = 3  # One cell filled, one empty (max possible sum: 3+6=9 >5)
    constraint = Constraint(
        ConstraintType.GT, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    # is_partial=True: still possible to reach sum >5
    assert board._check_constraint(constraint, [], is_partial=True) is True


def test_check_constraint_gt_partial_fail_max_possible_too_low():
    """Test that GT constraint fails for partial board when even max possible sum can't exceed required value."""
    board = Board(2, 2)
    board.board[0][0] = (
        0  # Even if we add 6, max sum is 6 which is only equal to 5 (not >5)
    )
    constraint = Constraint(
        ConstraintType.GT, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    # is_partial=True: max possible sum is 6, which is not >5 (wait, 0+6=6>5, let's use 0 and required 6)
    constraint2 = Constraint(
        ConstraintType.GT, [Position(row=0, col=0), Position(row=0, col=1)], 6
    )
    # is_partial=True: max possible sum is 6, which is not >6, so fails
    assert board._check_constraint(constraint2, [], is_partial=True) is False


def test_check_constraint_equal_partial_not_enough_available_dominoes():
    """Test that EQUAL constraint fails for partial board when there aren't enough available dots with the required value."""
    from domino import Domino

    board = Board(3, 2)
    board.board[0][0] = 3  # First cell has value 3, need two more 3s (total 3 cells)
    constraint = Constraint(
        ConstraintType.EQUAL,
        [Position(row=0, col=0), Position(row=0, col=1), Position(row=1, col=0)],
        3,
    )
    # We only have a domino with one 3, so we only have one more 3 available, but need two
    available_dominoes = [Domino(3, 4)]  # Only provides one additional 3
    assert (
        board._check_constraint(constraint, available_dominoes, is_partial=True)
        is False
    )


def test_generate_possible_dominoes_value_constraint(empty_board):
    """Test that generate_possible_dominoes correctly filters dominoes for VALUE constraint (lines 339-341)."""
    from domino import Domino

    # Add a VALUE constraint that cell (0,0) must be 3
    constraint = Constraint(ConstraintType.VALUE, [Position(row=0, col=0)], 3)
    empty_board.add_constraint(constraint)

    # Available dominoes - only those with a 3 should be possible
    available_dominoes = {Domino(3, 4), Domino(2, 5), Domino(3, 3), Domino(1, 2)}
    empty_board.generate_possible_dominoes(available_dominoes)

    # Only dominoes that contain a 3 should be possible
    possible = empty_board.possible_dominoes[0][0]
    assert possible == {Domino(3, 4), Domino(3, 3)}
    assert len(possible) == 2


def test_generate_possible_dominoes_lt_constraint(empty_board):
    """Test that generate_possible_dominoes correctly filters dominoes for LT constraint (lines 379-387)."""
    from domino import Domino

    # Add an LT constraint that sum of two cells must be < 8
    constraint = Constraint(
        ConstraintType.LT, [Position(row=0, col=0), Position(row=0, col=1)], 8
    )
    empty_board.add_constraint(constraint)

    # Available dominoes
    available_dominoes = {Domino(3, 4), Domino(2, 5), Domino(1, 2), Domino(5, 5)}
    empty_board.generate_possible_dominoes(available_dominoes)

    # All cells in the constraint should have the same filtered set
    possible00 = empty_board.possible_dominoes[0][0]
    possible01 = empty_board.possible_dominoes[0][1]
    assert possible00 == possible01
    # Only dominoes that can contribute to a sum < 8 should be possible
    assert len(possible00) > 0


def test_place_domino_rolls_back_on_partial_constraint_violation(empty_board):
    """Test that place_domino correctly rolls back if partial constraints are violated (covers lines 489-499)."""
    from direction import Direction
    from domino import Domino

    # Add a simple constraint that will be violated by our placement
    constraint = Constraint(
        ConstraintType.TOTAL, [Position(row=0, col=0), Position(row=0, col=1)], 5
    )
    empty_board.add_constraint(constraint)

    # Setup the specific domino we want to place in possible_dominoes
    # This ensures we pass the initial checks and reach the partial constraint check
    empty_board.possible_dominoes[0][0] = {
        Domino(1, 3)
    }  # Sum is 4, but constraint requires total 5 - wait, 1+3=4 <5, which will fail
    empty_board.possible_dominoes[0][1] = {Domino(1, 3)}

    available_dominoes = [Domino(1, 3), Domino(2, 3)]

    # Save original board state including colors and all other values
    orig_board00 = empty_board.board[0][0]
    orig_board01 = empty_board.board[0][1]
    orig_color00 = empty_board.cell_colors[0][0]
    orig_color01 = empty_board.cell_colors[0][1]
    orig_color_index = empty_board.color_index

    # Try to place the domino - this will pass the initial checks but fail the partial constraint check
    result = empty_board.place_domino(
        Domino(1, 3),
        Position(row=0, col=0),
        Direction.EAST,
        available_dominoes,
        Domino(1, 3),
    )

    # Placement should fail
    assert result is False
    # All values should be rolled back (this verifies lines 489-499 are executed)
    assert empty_board.board[0][0] == orig_board00
    assert empty_board.board[0][1] == orig_board01
    assert empty_board.cell_colors[0][0] == orig_color00
    assert empty_board.cell_colors[0][1] == orig_color01
    assert empty_board.color_index == orig_color_index


def test_place_domino_start_position_out_of_bounds(empty_board):
    """Test that place_domino fails when start position is outside board bounds."""
    from direction import Direction
    from domino import Domino

    # Try to place at (-1, -1) which is completely out of bounds
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=-1, col=-1),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_start_position_already_occupied(empty_board):
    """Test that place_domino fails when the start cell is already occupied."""
    from direction import Direction
    from domino import Domino

    # Occupy the start cell first
    empty_board.board[0][0] = 5
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_domino_not_possible_at_start(empty_board):
    """Test that place_domino fails when domino isn't in possible_dominoes for start position."""
    from direction import Direction
    from domino import Domino

    # Set possible dominoes to something else that doesn't include our domino or its reverse
    empty_board.possible_dominoes[0][0] = {Domino(3, 4)}
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_second_position_out_of_bounds_north(empty_board):
    """Test that place_domino fails when the second cell is out of bounds when direction is NORTH."""
    from direction import Direction
    from domino import Domino

    # Setup start position to have domino in possible_dominoes
    empty_board.possible_dominoes[0][0] = {Domino(1, 2)}
    # Try to place north from (0,0) - would go to (-1,0) which is out of bounds
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.NORTH,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_second_position_already_occupied(empty_board):
    """Test that place_domino fails when the second cell is already occupied."""
    from direction import Direction
    from domino import Domino

    # Setup possible dominoes
    empty_board.possible_dominoes[0][0] = {Domino(1, 2)}
    empty_board.possible_dominoes[0][1] = {Domino(1, 2)}
    # Occupy the second cell first
    empty_board.board[0][1] = 5
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_domino_not_possible_at_second(empty_board):
    """Test that place_domino fails when domino isn't in possible_dominoes for second position."""
    from direction import Direction
    from domino import Domino

    # Setup only the first cell to have the domino in possible_dominoes
    empty_board.possible_dominoes[0][0] = {Domino(1, 2)}
    empty_board.possible_dominoes[0][1] = {Domino(3, 4)}  # Different domino
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_reversed_domino_accepted(empty_board):
    """Test that place_domino accepts reversed domino if it's in possible_dominoes."""
    from direction import Direction
    from domino import Domino

    # Allow reversed domino
    empty_board.possible_dominoes[0][0] = {Domino(2, 1)}  # This is reverse of (1,2)
    empty_board.possible_dominoes[0][1] = {Domino(2, 1)}

    # This should still work because reverse_domino is checked
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is True


def test_place_domino_successfully_places_valid_domino(empty_board):
    """Test that place_domino successfully places a valid domino."""
    from direction import Direction
    from domino import Domino

    # Set everything up correctly for a successful placement
    empty_board.possible_dominoes[0][0] = {Domino(1, 2)}
    empty_board.possible_dominoes[0][1] = {Domino(1, 2)}
    available_dominoes = [Domino(1, 2)]

    # Save original state
    orig_color_index = empty_board.color_index

    # Place the domino
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        available_dominoes,
        Domino(1, 2),
    )

    # Placement should succeed
    assert result is True
    # Board values should be updated
    assert empty_board.board[0][0] == 1
    assert empty_board.board[0][1] == 2
    # Color index should be incremented
    assert empty_board.color_index == (orig_color_index + 1) % len(
        empty_board.cell_colors[0]
    )


def test_place_domino_success_with_all_directions(empty_board):
    """Test that place_domino works with all four directions."""
    from direction import Direction
    from domino import Domino

    # Test EAST
    empty_board.possible_dominoes[0][0] = {Domino(1, 2)}
    empty_board.possible_dominoes[0][1] = {Domino(1, 2)}
    result1 = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result1 is True

    # Reset board for next test
    empty_board.board[0][0] = None
    empty_board.board[0][1] = None
    empty_board.color_index = 0

    # Test SOUTH
    empty_board.possible_dominoes[1][0] = {Domino(3, 4)}
    empty_board.possible_dominoes[0][0] = {Domino(3, 4)}
    result2 = empty_board.place_domino(
        Domino(3, 4),
        Position(row=0, col=0),
        Direction.SOUTH,
        [Domino(3, 4)],
        Domino(3, 4),
    )
    assert result2 is True

    # Reset board for WEST test
    empty_board.board[0][0] = None
    empty_board.board[1][0] = None
    empty_board.color_index = 0

    # Test WEST
    empty_board.possible_dominoes[0][1] = {Domino(5, 6)}
    empty_board.possible_dominoes[0][0] = {Domino(5, 6)}
    result3 = empty_board.place_domino(
        Domino(5, 6),
        Position(row=0, col=1),
        Direction.WEST,
        [Domino(5, 6)],
        Domino(5, 6),
    )
    assert result3 is True

    # Reset board for NORTH test
    empty_board.board[0][1] = None
    empty_board.board[0][0] = None
    empty_board.color_index = 0

    # Test NORTH
    empty_board.possible_dominoes[1][0] = {Domino(4, 5)}
    empty_board.possible_dominoes[0][0] = {Domino(4, 5)}
    result4 = empty_board.place_domino(
        Domino(4, 5),
        Position(row=1, col=0),
        Direction.NORTH,
        [Domino(4, 5)],
        Domino(4, 5),
    )
    assert result4 is True
    from domino import Domino

    # Try to place domino starting at row -1 which is out of bounds
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=-1, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False

    # Try to place domino starting beyond board dimensions
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=100, col=100),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_start_position_already_occupied(empty_board):
    """Test that place_domino fails when starting position is already occupied."""
    from direction import Direction
    from domino import Domino

    # Occupy the starting cell
    empty_board.board[0][0] = 5

    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_domino_not_possible_at_start(empty_board):
    """Test that place_domino fails when domino is not in possible_dominoes for start position."""
    from direction import Direction
    from domino import Domino

    # Make only certain dominoes possible at (0,0)
    empty_board.possible_dominoes[0][0] = {Domino(3, 4), Domino(5, 6)}

    # Try to place a domino that's not in possible_dominoes
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_end_position_out_of_bounds(empty_board):
    """Test that place_domino fails when end position is out of bounds."""
    from direction import Direction
    from domino import Domino

    # First set possible dominoes so the initial checks pass
    empty_board.possible_dominoes[0][0] = {Domino(1, 2)}
    empty_board.possible_dominoes[0][1] = {Domino(1, 2)}

    # Try to place north from (0,0) - would go to row -1
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.NORTH,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False

    # Try to place west from (0,0) - would go to col -1
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.WEST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_end_position_already_occupied(empty_board):
    """Test that place_domino fails when end position is already occupied."""
    from direction import Direction
    from domino import Domino

    # Set possible dominoes
    empty_board.possible_dominoes[0][0] = {Domino(1, 2)}
    empty_board.possible_dominoes[0][1] = {Domino(1, 2)}
    # Occupy the end cell
    empty_board.board[0][1] = 5

    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_domino_not_possible_at_end(empty_board):
    """Test that place_domino fails when domino is not in possible_dominoes for end position."""
    from direction import Direction
    from domino import Domino

    # Make domino possible at start but not at end
    empty_board.possible_dominoes[0][0] = {Domino(1, 2)}
    empty_board.possible_dominoes[0][1] = {Domino(3, 4)}  # Different dominoes allowed

    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is False


def test_place_domino_reversed_domino_accepted(empty_board):
    """Test that place_domino accepts reversed domino if it's in possible_dominoes."""
    from direction import Direction
    from domino import Domino

    # Allow reversed domino
    empty_board.possible_dominoes[0][0] = {Domino(2, 1)}  # This is reverse of (1,2)
    empty_board.possible_dominoes[0][1] = {Domino(2, 1)}

    # This should still work because reverse_domino is checked
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is True


def test_place_domino_successfully_places_valid_domino(empty_board):
    """Test that place_domino successfully places a valid domino."""
    from direction import Direction
    from domino import Domino

    # Set everything up correctly for a successful placement
    empty_board.possible_dominoes[0][0] = {Domino(1, 2)}
    empty_board.possible_dominoes[0][1] = {Domino(1, 2)}
    available_dominoes = [Domino(1, 2)]

    # Save original state
    orig_color_index = empty_board.color_index

    # Place the domino
    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.EAST,
        available_dominoes,
        Domino(1, 2),
    )

    # Placement should succeed
    assert result is True
    # Board values should be updated
    assert empty_board.board[0][0] == 1
    assert empty_board.board[0][1] == 2
    # Color index should be incremented
    assert empty_board.color_index == (orig_color_index + 1) % len(
        empty_board.cell_colors[0]
    )


def test_place_domino_all_directions_work(empty_board):
    """Test that place_domino works with all four directions."""
    from direction import Direction
    from domino import Domino

    # Test EAST (already tested, but test SOUTH here)
    empty_board.possible_dominoes[0][0] = {Domino(1, 2)}
    empty_board.possible_dominoes[1][0] = {Domino(1, 2)}  # cell below (0,0)

    result = empty_board.place_domino(
        Domino(1, 2),
        Position(row=0, col=0),
        Direction.SOUTH,
        [Domino(1, 2)],
        Domino(1, 2),
    )
    assert result is True


def test_repr_handles_all_cell_cases(empty_board):
    """Test that __repr__ correctly handles all cell cases (lines 668-679)."""
    # Setup various cell types to test all conditions in __repr__
    # Fill board with different cell states
    empty_board.board[0][0] = -1  # blocked cell
    empty_board.board[0][1] = 5  # occupied cell with value
    empty_board.board[1][0] = None  # empty cell
    empty_board.board[1][1] = 3  # another occupied cell

    # Get the string representation
    repr_str = repr(empty_board)

    # Verify the string is properly formatted
    assert isinstance(repr_str, str)
    assert "|" in repr_str  # Should contain pipe separators
    assert " ." in repr_str  # Should contain empty cell marker
    # Even though the colored text has ANSI codes, the structure should be correct
    assert len(repr_str.split("\n")) > 1  # Should have multiple lines for the grid


def test_repr_with_occupied_blocked_and_empty_cells(empty_board):
    """Test __repr__ correctly formats mixed cell states (covers all branches)."""
    # Fill the board with all three cell types
    empty_board.board[0][0] = -1  # blocked
    empty_board.board[0][1] = 3  # occupied
    empty_board.board[1][0] = -1  # blocked
    empty_board.board[1][1] = 6  # occupied

    # Generate representation
    output = repr(empty_board)

    # Verify all cell types are represented in the string
    lines = output.strip().split("\n")
    assert len(lines) == empty_board.n_row  # Should have one line per row
    for line in lines:
        assert line.startswith("|")  # Each row starts with a pipe
        assert line.endswith("|")  # Each row ends with a pipe


def test_repr_contains_correct_number_of_cells(empty_board):
    """Verify that __repr__ has the correct number of cells per row."""
    # Fill board completely with values to ensure all cells are processed
    for i in range(empty_board.n_row):
        for j in range(empty_board.n_col):
            empty_board.board[i][j] = i * j + 1

    # Generate repr
    repr_str = repr(empty_board)
    lines = repr_str.strip().split("\n")

    # Check each row has the correct number of cells
    for line in lines:
        cells = line.strip("|").split("|")
        assert len(cells) == empty_board.n_col
