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
    assert isinstance(dominoes, set)
    assert dominoes == {Domino(1, 2), Domino(3, 4)}

    # Check a few constraints to be sure
    # Constraint A
    assert board.constraints[0][0] == (ConstraintType.LT, 5)
    # Constraint x (DEAD)
    assert board.constraints[1][0] == (ConstraintType.DEAD, -1)
    # Constraint . (FREE)
    assert board.constraints[0][1] == (ConstraintType.FREE, None)
    # Constraint E (EQUAL)
    assert board.constraints[1][1] == (ConstraintType.EQUAL, 0)
    # Constraint C (TOTAL)
    assert board.constraints[1][2] == (ConstraintType.TOTAL, 3)


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
    with pytest.raises(tomllib.TOMLDecodeError):
        read_toml(filename)

def test_read_toml_missing_board(create_test_toml):
    content = """
[constraints]
A = "<5"

[dominoes]
tiles = ["12"]
"""
    filename = create_test_toml(content)
    with pytest.raises(KeyError):
        read_toml(filename)

def test_read_toml_missing_constraints(create_test_toml):
    content = """
[board]
layout = ["A.B"]

[dominoes]
tiles = ["12"]
"""
    filename = create_test_toml(content)
    with pytest.raises(KeyError):
        read_toml(filename)

def test_read_toml_missing_dominoes(create_test_toml):
    content = """
[board]
layout = ["A.B"]

[constraints]
A = "<5"
"""
    filename = create_test_toml(content)
    with pytest.raises(KeyError):
        read_toml(filename)


def test_read_csv_success():
    board, dominoes = read_csv("test.csv")
    assert isinstance(board, Board)
    assert board.n_row == 5
    assert board.n_col == 6
    assert isinstance(dominoes, set)
    assert dominoes == {Domino(5, 4), Domino(0, 0), Domino(2, 2), Domino(5, 0), Domino(1, 3), Domino(2, 0), Domino(0, 1), Domino(4, 2), Domino(3, 3), Domino(1, 5), Domino(3, 0)}

def test_read_csv_success2():
    board, dominoes = read_csv("test_csv2.csv")
    assert isinstance(board, Board)
    assert board.n_row == 3
    assert board.n_col == 6
    assert isinstance(dominoes, set)
    assert dominoes == {Domino(4, 2), Domino(1, 1), Domino(0, 2), Domino(4, 5), Domino(2, 6), Domino(1, 5), Domino(1, 0)}

def test_read_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_csv("non_existent_file.csv")