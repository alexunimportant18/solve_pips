import tomllib

import pytest

from board import Board
from constraint import ConstraintType
from domino import Domino
from readfile import read_csv, read_toml


@pytest.fixture
def create_test_toml(tmp_path):
    def _create_file(content):
        path = tmp_path / "test_config.toml"
        path.write_text(content)
        return str(path)

    return _create_file


def test_read_toml_success(create_test_toml):
    content = """
[board]
layout = [
  "A.B",
  "xEC",
]

[constraints]
A = "<5"
B = ">2"
C = "+3"
E = "=="

[dominoes]
tiles = [
  "12",
  "34",
]
"""
    filename = create_test_toml(content)
    board, dominoes = read_toml(filename)

    assert isinstance(board, Board)
    assert board.n_row == 2
    assert board.n_col == 3
    assert isinstance(dominoes, list)
    assert set(dominoes) == {Domino(1, 2), Domino(3, 4)}

    # Check a few constraints to be sure
    # Constraint A
    assert board.constraints[0][0].constraint_type == ConstraintType.LT
    # Constraint x (DEAD)
    assert board.constraints[1][0].constraint_type == ConstraintType.DEAD
    # Constraint . (FREE)
    assert board.constraints[0][1].constraint_type == ConstraintType.FREE
    # Constraint E (EQUAL)
    assert board.constraints[1][1].constraint_type == ConstraintType.EQUAL
    # Constraint C (TOTAL)
    assert board.constraints[1][2].constraint_type == ConstraintType.TOTAL


def test_read_toml_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_toml("non_existent_file.toml")


def test_read_toml_invalid_toml(create_test_toml):
    content = """
board = [
  "A.B"
  "xEC",
]
"""
    filename = create_test_toml(content)
    with pytest.raises(ValueError):
        read_toml(filename)


def test_read_toml_missing_board(create_test_toml):
    content = """
[constraints]
A = "<5"

[dominoes]
tiles = ["12"]
"""
    filename = create_test_toml(content)
    with pytest.raises(ValueError):
        read_toml(filename)


def test_read_toml_missing_constraints(create_test_toml):
    content = """
[board]
layout = ["A.B"]

[dominoes]
tiles = ["12"]
"""
    filename = create_test_toml(content)
    # The current refactored read_toml handles missing 'constraints' as an empty dict
    board, dominoes = read_toml(filename)
    assert isinstance(board, Board)


def test_read_toml_missing_dominoes(create_test_toml):
    content = """
[board]
layout = ["A.B"]

[constraints]
A = "<5"
"""
    filename = create_test_toml(content)
    with pytest.raises(ValueError):
        read_toml(filename)


def test_read_csv_success():
    # Assuming test.csv exists in root
    try:
        board, dominoes = read_csv("easy.csv")
        assert isinstance(board, Board)
        assert isinstance(dominoes, list)
    except FileNotFoundError:
        pytest.skip("test.csv not found")


def test_read_csv_success2():
    # Assuming test_csv2.csv exists in root
    try:
        board, dominoes = read_csv("medium.csv")
        assert isinstance(board, Board)
        assert isinstance(dominoes, list)
    except FileNotFoundError:
        pytest.skip("test_csv2.csv not found")


def test_read_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_csv("non_existent_file.csv")


def test_is_valid_constraint():
    """Test the is_valid_constraint function covers all cases."""
    from readfile import is_valid_constraint

    # Test empty string
    assert is_valid_constraint("") == False
    assert is_valid_constraint("   ") == False

    # Test valid digits (0-6)
    assert is_valid_constraint("0") == True
    assert is_valid_constraint("3") == True
    assert is_valid_constraint("6") == True
    assert is_valid_constraint("7") == False  # 7 is invalid
    assert is_valid_constraint("-1") == False

    # Test . and X/x
    assert is_valid_constraint(".") == True
    assert is_valid_constraint("X") == True
    assert is_valid_constraint("x") == True

    # Test constraints that are too short
    assert is_valid_constraint("a") == False  # single char, not digit/.x
    assert is_valid_constraint("<") == False  # single operator

    # Test invalid operator
    assert is_valid_constraint("a?5") == False  # unknown operator

    # Test = and ! constraints
    # Valid cases: "a=", "a=="
    assert is_valid_constraint("a=") == True  # len 2, starts with alpha
    assert is_valid_constraint("A!") == True
    assert is_valid_constraint("a==") == True  # len 3, ends with =
    assert is_valid_constraint("A!=") == True

    # Invalid =/! cases
    assert is_valid_constraint("1=") == False  # starts with digit, not alpha
    assert is_valid_constraint("a==x") == False  # len >3, invalid suffix
    assert is_valid_constraint("a!x") == False  # third char not = for len 3
    assert is_valid_constraint("=") == False  # just =

    # Test other operators (<, >, +) - need len >=3, starts with alpha, rest digits
    assert is_valid_constraint("a<5") == True
    assert is_valid_constraint("A>10") == True
    assert is_valid_constraint("b+3") == True
    assert is_valid_constraint("1<5") == False  # starts with digit
    assert is_valid_constraint("a<x") == False  # suffix not digits
    assert is_valid_constraint("a<") == False  # len 2, missing suffix


def test_get_puzzle_reader():
    """Test the get_puzzle_reader factory function."""
    from readfile import CsvPuzzleReader, TomlPuzzleReader, get_puzzle_reader

    # Test toml extension
    reader = get_puzzle_reader("test.toml")
    assert isinstance(reader, TomlPuzzleReader)

    # Test csv extension
    reader = get_puzzle_reader("test.csv")
    assert isinstance(reader, CsvPuzzleReader)

    # Test unsupported extension
    with pytest.raises(ValueError, match="Unsupported format"):
        get_puzzle_reader("test.txt")


def test_toml_reader_invalid_constraint_key(create_test_toml):
    """Test TomlPuzzleReader raises error for invalid constraint keys."""
    content = """
[board]
layout = ["A.B"]

[constraints]
123 = "<5"  # invalid key (not alpha)

[dominoes]
tiles = ["12"]
"""
    filename = create_test_toml(content)
    with pytest.raises(ValueError, match="Invalid constraint specification"):
        read_toml(filename)


def test_toml_reader_constraint_key_not_found(create_test_toml):
    """Test TomlPuzzleReader raises error if constraint key not in layout."""
    content = """
[board]
layout = [".B."]

[constraints]
A = "<5"  # A not in layout

[dominoes]
tiles = ["12"]
"""
    filename = create_test_toml(content)
    with pytest.raises(ValueError, match="Constraint key 'A' not found in layout"):
        read_toml(filename)


@pytest.fixture
def create_test_csv(tmp_path):
    def _create_file(content):
        path = tmp_path / "test.csv"
        path.write_text(content)
        return str(path)

    return _create_file


def test_csv_reader_success(create_test_csv):
    """Test CsvPuzzleReader reads a valid CSV file correctly."""
    # First line: dominoes, then layout lines with proper CSV formatting
    # All cell constraints are valid: digits, ., x, and constraint formats like B<3, C+7, D==, E!=
    content = """13,24,00
5,B<3,C+7
x,.,D==,E!=
"""
    filename = create_test_csv(content)
    from readfile import read_csv

    board, dominoes = read_csv(filename)

    assert isinstance(board, Board)
    assert board.n_row == 2  # two layout lines after dominoes
    assert board.n_col == 4  # max columns in layout
    assert set(dominoes) == {Domino(1, 3), Domino(2, 4), Domino(0, 0)}

    # Check DEAD cell (x at row1, col0)
    assert board.constraints[1][0].constraint_type == ConstraintType.DEAD
    # Check FREE cell (.) at row1, col1
    assert board.constraints[1][1].constraint_type == ConstraintType.FREE
    # Check VALUE cell (5 at row0, col0)
    assert board.constraints[0][0].constraint_type == ConstraintType.VALUE
    assert board.constraints[0][0].value == 5
    # Check LT constraint (B<3 at row0, col1)
    assert board.constraints[0][1].constraint_type == ConstraintType.LT
    # Check TOTAL constraint (C+7 at row0, col2)
    assert board.constraints[0][2].constraint_type == ConstraintType.TOTAL
    # Check EQUAL constraint (D== at row1, col2)
    assert board.constraints[1][2].constraint_type == ConstraintType.EQUAL
    # Check NE constraint (E!= at row1, col3)
    assert board.constraints[1][3].constraint_type == ConstraintType.NE


def test_csv_reader_empty_file(create_test_csv):
    """Test CsvPuzzleReader raises error for empty CSV."""
    filename = create_test_csv("")
    from readfile import read_csv

    with pytest.raises(ValueError, match="Empty CSV file"):
        read_csv(filename)


def test_csv_reader_no_valid_dominoes(create_test_csv):
    """Test CsvPuzzleReader raises error if no valid dominoes found."""
    content = """abc,def
12,34
"""
    filename = create_test_csv(content)
    from readfile import read_csv

    with pytest.raises(ValueError, match="No valid dominoes found"):
        read_csv(filename)


def test_csv_reader_empty_cell(create_test_csv):
    """Test CsvPuzzleReader raises error for empty cell in layout."""
    # First line: dominoes (each domino is a separate CSV cell, two digits each)
    # Second line: layout with an empty cell (,,) to trigger the error
    content = """12,34
1,,3
"""
    filename = create_test_csv(content)
    from readfile import read_csv

    with pytest.raises(ValueError, match="Error reading CSV.*Empty cell at"):
        read_csv(filename)


def test_csv_reader_invalid_constraint(create_test_csv):
    """Test CsvPuzzleReader raises error for invalid constraint in layout."""
    # First line: valid dominoes
    # Second line: layout with 'abc' which is an invalid constraint
    content = """12,34
1,abc,3
"""
    filename = create_test_csv(content)
    from readfile import read_csv

    with pytest.raises(
        ValueError, match="Error reading CSV.*Invalid constraint 'abc' at"
    ):
        read_csv(filename)


def test_toml_reader_empty_layout(create_test_toml):
    """Test TomlPuzzleReader handles empty layout."""
    content = """
[board]
layout = []

[dominoes]
tiles = ["12"]
"""
    filename = create_test_toml(content)
    board, dominoes = read_toml(filename)
    assert board.n_row == 0
    assert board.n_col == 0


def test_toml_reader_invalid_domino_format(create_test_toml):
    """Test TomlPuzzleReader skips invalid domino entries."""
    content = """
[board]
layout = ["..."]

[dominoes]
tiles = ["12", "abc", "x", "34"]
"""
    filename = create_test_toml(content)
    board, dominoes = read_toml(filename)
    assert set(dominoes) == {Domino(1, 2), Domino(3, 4)}  # only valid ones
