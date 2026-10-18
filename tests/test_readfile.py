import pytest
import tomllib
from readfile import read_toml, read_csv
from board import Board
from domino import Domino
from constraint import ConstraintType

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
        board, dominoes = read_csv("test.csv")
        assert isinstance(board, Board)
        assert isinstance(dominoes, list)
    except FileNotFoundError:
        pytest.skip("test.csv not found")

def test_read_csv_success2():
    # Assuming test_csv2.csv exists in root
    try:
        board, dominoes = read_csv("test_csv2.csv")
        assert isinstance(board, Board)
        assert isinstance(dominoes, list)
    except FileNotFoundError:
        pytest.skip("test_csv2.csv not found")

def test_read_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_csv("non_existent_file.csv")
