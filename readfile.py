import csv
import tomllib
from abc import ABC, abstractmethod
from curses.ascii import isalpha, isdigit

from board import Board
from constraint import Constraint, ConstraintType
from domino import Domino
from position import Position

CONSTRAINT_TYPE_MAP = {
    "<": ConstraintType.LT,
    ">": ConstraintType.GT,
    "+": ConstraintType.TOTAL,
    "=": ConstraintType.EQUAL,
    "!": ConstraintType.NE,
}


def is_valid_constraint(constraint: str) -> bool:
    constraint = constraint.strip()
    # empty cell, return false
    if not constraint:
        return False

    # VALUE constraint
    if constraint.isdigit() and int(constraint) <= 6 and int(constraint) >= 0:
        return True

    # FREE constraint or DEAD constraint
    if constraint == "." or constraint.upper() == "X":
        return True

    # All other operators should have at least 2 character
    if len(constraint) < 2:
        return False

    # For other constraints, check if the second character is a value operator
    if constraint[1] not in CONSTRAINT_TYPE_MAP:
        return False

    if constraint[1] in ("=", "!"):
        if len(constraint) > 3:
            return False
        if len(constraint) == 3:
            return constraint[2] == "="
        if len(constraint) == 2:
            if constraint[0].upper().isalpha():
                return True
            else:
                return False

    # All other constraints should have a value after the operator
    if len(constraint) < 3:
        return False
    if not constraint[0].upper().isalpha():
        return False
    if not constraint[2:].isdigit():
        return False

    return True


class PipsPuzzleReader(ABC):
    @abstractmethod
    def read(self, filename: str) -> tuple[Board, list[Domino]]:
        """Reads a puzzle file and returns a Board and a list of Dominoes."""
        pass


class TomlPuzzleReader(PipsPuzzleReader):
    def read(self, filename: str) -> tuple[Board, list[Domino]]:
        try:
            with open(filename, "rb") as f:
                config = tomllib.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Puzzle file not found: {filename}")
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML format in {filename}: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error reading {filename}: {e}")

        try:
            lines = config["board"]["layout"]
            height = len(lines)
            width = len(lines[0]) if lines else 0
            board = Board(width=width, height=height)
            cells = [list(line) for line in lines]
            for row in cells:
                for col in row:
                    if (
                        col not in CONSTRAINT_TYPE_MAP.keys()
                        and col.upper() not in (".", "X")
                        and not col.isdigit()
                    ):
                        raise ValueError(
                            f"Invalid constraint operator '{col}' in board layout."
                        )
        except KeyError as e:
            raise KeyError(f"Missing required TOML section: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing board layout in {filename}: {e}")

        try:
            constraints = config["constraints"]
            for k, v in constraints.items():
                if not k.upper().isalpha():
                    raise ValueError(
                        f"Constraint key '{k}' must be an alphabetical character."
                    )

                if v[0] not in CONSTRAINT_TYPE_MAP:
                    raise ValueError(
                        f"Invalid constraint operator '{v[0]}' for key '{k}'. Valid operators: {list(CONSTRAINT_TYPE_MAP.keys())}"
                    )

                constraint_type = CONSTRAINT_TYPE_MAP[v[0]]
                value_str = 0 if v[0] in ("=", "!") else v[1:]

                try:
                    value = int(value_str)
                except ValueError:
                    raise ValueError(
                        f"Invalid numeric value '{value_str}' for constraint key '{k}'."
                    )

                position_list = []
                for i, row in enumerate(cells):
                    for j, cell in enumerate(row):
                        if cell == k:
                            position_list.append(Position(row=i, col=j))

                if not position_list:
                    raise ValueError(f"Constraint key '{k}' not found in board layout.")

                board.add_constraint(Constraint(constraint_type, position_list, value))
        except KeyError:
            raise KeyError(f"Missing 'constraints' section in {filename}")
        except ValueError as e:
            raise e

        try:
            # handle DEAD cells
            dead_positions = []
            for i, row in enumerate(cells):
                for j, cell in enumerate(row):
                    if cell.upper() == "X":
                        dead_positions.append(Position(row=i, col=j))
            if dead_positions:
                board.add_constraint(
                    Constraint(ConstraintType.DEAD, dead_positions, -1)
                )

            # handle FREE cells
            free_positions = []
            for i, row in enumerate(cells):
                for j, cell in enumerate(row):
                    if cell == ".":
                        free_positions.append(Position(row=i, col=j))
            if free_positions:
                board.add_constraint(
                    Constraint(ConstraintType.FREE, free_positions, None)
                )

            # handle VALUE cells
            for i, row in enumerate(cells):
                for j, cell in enumerate(row):
                    if cell.isdigit():
                        board.add_constraint(
                            Constraint(
                                ConstraintType.VALUE,
                                [Position(row=i, col=j)],
                                int(cell),
                            )
                        )
        except Exception as e:
            raise ValueError(f"Error processing layout markers in {filename}: {e}")

        try:
            dominoes = []
            tiles = config["dominoes"]["tiles"]
            for v in tiles:
                if not isinstance(v, str) or len(v) < 2:
                    raise ValueError(
                        f"Invalid domino tile definition '{v}'. Expected a string of at least 2 digits."
                    )

                if not (v[0].isdigit() and v[1].isdigit()):
                    raise ValueError(f"Domino tile '{v}' must start with two digits.")

                dominoes.append(Domino(int(v[0]), int(v[1])))
        except KeyError:
            raise KeyError(f"Missing 'dominoes' section or 'tiles' list in {filename}")
        except ValueError as e:
            raise e

        return board, dominoes


class CsvPuzzleReader(PipsPuzzleReader):
    def read(self, filename: str) -> tuple[Board, list[Domino]]:
        dominoes = []
        cell_map = {}
        width, height = 0, 0

        try:
            with open(filename, mode="r") as file:
                reader = csv.reader(file)
                for i, line in enumerate(reader):
                    # Skip truly empty lines (like at the end of the file)
                    if not line or not any(cell.strip() for cell in line):
                        continue
                    if i == 0:
                        for cell in line:
                            cell = cell.strip()
                            if not cell:
                                continue
                            if len(cell) < 2 or not (
                                cell[0].isdigit() and cell[1].isdigit()
                            ):
                                raise ValueError(
                                    f"Invalid domino tile '{cell}' at the start of {filename}. Expected 2 digits."
                                )
                            dominoes.append(Domino(int(cell[0]), int(cell[1])))
                    else:
                        row = i - 1
                        for col, cell in enumerate(line):
                            cell = cell.strip()
                            if not cell:
                                raise ValueError(
                                    f"Empty cell at position ({row}, {col}) in {filename}"
                                )
                            width = max(width, col + 1)
                            height = max(height, row + 1)
                            if is_valid_constraint(cell):
                                if cell in cell_map:
                                    cell_map[cell].append(Position(row=row, col=col))
                                else:
                                    cell_map[cell] = [Position(row=row, col=col)]
                            else:
                                raise ValueError(
                                    f"Invalid constraint '{cell}' at position ({row}, {col}) in {filename}"
                                )
        except FileNotFoundError:
            raise FileNotFoundError(f"Puzzle file not found: {filename}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise RuntimeError(f"Unexpected error reading CSV {filename}: {e}")

        if not dominoes:
            raise ValueError(f"No dominoes found in the first line of {filename}")
        if height == 0:
            raise ValueError(f"No board layout found in {filename}")

        # print(f"cell_map={cell_map}")
        board = Board(width=width, height=height)
        for k, v in cell_map.items():
            if k == ".":
                board.add_constraint(Constraint(ConstraintType.FREE, v, None))
            elif k == "x":
                board.add_constraint(Constraint(ConstraintType.DEAD, v, -1))
            elif k.isdigit():
                board.add_constraint(Constraint(ConstraintType.VALUE, v, int(k)))
            else:
                try:
                    # CSV constraints are usually formatted as 'A+1' where A is the key and +1 is the spec
                    if len(k) < 2:
                        raise ValueError(
                            f"Constraint key '{k}' is too short to be a valid constraint."
                        )

                    key = k[0]
                    spec = k[1:]

                    if not spec or spec[0] not in CONSTRAINT_TYPE_MAP:
                        raise ValueError(
                            f"Invalid constraint operator in '{k}'. Valid operators: {list(CONSTRAINT_TYPE_MAP.keys())}"
                        )

                    constraint_type = CONSTRAINT_TYPE_MAP[spec[0]]
                    value_str = "0" if spec[0] in ("=", "!") else spec[1:]

                    try:
                        value = int(value_str)
                    except ValueError:
                        raise ValueError(f"Invalid numeric value in constraint '{k}'.")

                    board.add_constraint(Constraint(constraint_type, v, value))
                except Exception as e:
                    raise ValueError(
                        f"Error reading input file: {e} at position ({v[0].row}, {v[0].col})"
                    )

        return board, dominoes


def get_puzzle_reader(filename: str) -> PipsPuzzleReader:
    if filename.endswith(".toml"):
        return TomlPuzzleReader()
    elif filename.endswith(".csv"):
        return CsvPuzzleReader()
    else:
        raise ValueError(f"Unsupported file format: {filename}")


# Legacy support for read_toml and read_csv functions
def read_toml(filename: str) -> tuple[Board, list[Domino]]:
    return TomlPuzzleReader().read(filename)


def read_csv(filename: str) -> tuple[Board, list[Domino]]:
    return CsvPuzzleReader().read(filename)
