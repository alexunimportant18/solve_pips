import csv
import tomllib
from abc import ABC, abstractmethod

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
    """Validates if a string represents a valid puzzle constraint.

    Args:
        constraint (str): The constraint string to validate.

    Returns:
        bool: True if the constraint is valid, False otherwise.
    """
    constraint = constraint.strip()
    if not constraint:
        return False
    if constraint.isdigit() and 0 <= int(constraint) <= 6:
        return True
    if constraint == "." or constraint.upper() == "X":
        return True
    if len(constraint) < 2:
        return False
    if constraint[1] not in CONSTRAINT_TYPE_MAP:
        return False
    if constraint[1] in ("=", "!"):
        if len(constraint) == 2:
            return constraint[0].isalpha()
        if len(constraint) == 3:
            return constraint[2] == "="
        return False
    return len(constraint) >= 3 and constraint[0].isalpha() and constraint[2:].isdigit()


class PipsPuzzleReader(ABC):
    """Abstract base class for puzzle file readers."""

    @abstractmethod
    def read(self, filename: str) -> tuple[Board, list[Domino]]:
        """Reads a puzzle file and returns the board and dominoes.

        Args:
            filename (str): Path to the puzzle file.

        Returns:
            tuple[Board, list[Domino]]: A tuple containing the Board object and list of Dominoes.
        """
        pass


class TomlPuzzleReader(PipsPuzzleReader):
    """Reader for puzzle definitions in TOML format."""

    def read(self, filename: str) -> tuple[Board, list[Domino]]:
        """Parses a TOML file to generate a Board and a list of Dominoes.

        Args:
            filename (str): Path to the TOML puzzle file.

        Returns:
            tuple[Board, list[Domino]]: The parsed Board and Dominoes.

        Raises:
            ValueError: If the TOML structure is invalid or contains parsing errors.
            FileNotFoundError: If the file does not exist.
        """
        try:
            with open(filename, "rb") as f:
                config = tomllib.load(f)
        except (FileNotFoundError, tomllib.TOMLDecodeError) as e:
            raise type(e)(f"Error reading {filename}: {e}")

        try:
            lines = config["board"]["layout"]
            height, width = len(lines), len(lines[0]) if lines else 0
            board = Board(width=width, height=height)
            cells = [list(line) for line in lines]

            # Process explicit constraints from the 'constraints' section
            for k, v in config.get("constraints", {}).items():
                if not k.isalpha() or v[0] not in CONSTRAINT_TYPE_MAP:
                    raise ValueError(f"Invalid constraint specification for {k}: {v}")

                val_str = "0" if v[0] in ("=", "!") else v[1:]
                positions = [
                    Position(row=r, col=c)
                    for r, row in enumerate(cells)
                    for c, cell in enumerate(row)
                    if cell == k
                ]
                if not positions:
                    raise ValueError(f"Constraint key '{k}' not found in layout")

                board.add_constraint(
                    Constraint(CONSTRAINT_TYPE_MAP[v[0]], positions, int(val_str))
                )

            # Process layout markers
            for r, row in enumerate(cells):
                for c, cell in enumerate(row):
                    if cell == ".":
                        board.add_constraint(
                            Constraint(
                                ConstraintType.FREE, [Position(row=r, col=c)], None
                            )
                        )
                    elif cell.upper() == "X":
                        board.add_constraint(
                            Constraint(
                                ConstraintType.DEAD, [Position(row=r, col=c)], -1
                            )
                        )
                    elif cell.isdigit():
                        board.add_constraint(
                            Constraint(
                                ConstraintType.VALUE,
                                [Position(row=r, col=c)],
                                int(cell),
                            )
                        )

            dominoes = [
                Domino(int(t[0]), int(t[1]))
                for t in config["dominoes"]["tiles"]
                if len(t) >= 2 and t[:2].isdigit()
            ]
            return board, dominoes
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error parsing TOML layout in {filename}: {e}")


class CsvPuzzleReader(PipsPuzzleReader):
    """Reader for puzzle definitions in CSV format."""

    def read(self, filename: str) -> tuple[Board, list[Domino]]:
        """Parses a CSV file to generate a Board and a list of Dominoes.

        Args:
            filename (str): Path to the CSV puzzle file.

        Returns:
            tuple[Board, list[Domino]]: The parsed Board and Dominoes.

        Raises:
            ValueError: If the CSV format is invalid or contains parsing errors.
            FileNotFoundError: If the file does not exist.
        """
        try:
            with open(filename, mode="r") as file:
                reader = list(csv.reader(file))
                if not reader:
                    raise ValueError("Empty CSV file")

                # First line: Dominoes
                dominoes = [
                    Domino(int(c[0]), int(c[1]))
                    for c in reader[0]
                    if c.strip() and len(c.strip()) >= 2 and c.strip()[:2].isdigit()
                ]
                if not dominoes:
                    raise ValueError("No valid dominoes found")

                # Remaining lines: Layout
                cell_map = {}
                height = 0
                width = 0
                for r, line in enumerate(reader[1:]):
                    if not line or not any(c.strip() for c in line):
                        continue
                    height += 1
                    width = max(width, len(line))
                    for c, cell in enumerate(line):
                        cell = cell.strip()
                        if not cell:
                            raise ValueError(f"Empty cell at ({r}, {c})")
                        if not is_valid_constraint(cell):
                            raise ValueError(
                                f"Invalid constraint '{cell}' at ({r}, {c})"
                            )
                        cell_map.setdefault(cell, []).append(Position(row=r, col=c))

                board = Board(width=width, height=height)
                for k, v in cell_map.items():
                    if k == ".":
                        board.add_constraint(Constraint(ConstraintType.FREE, v, None))
                    elif k.lower() == "x":
                        board.add_constraint(Constraint(ConstraintType.DEAD, v, -1))
                    elif k.isdigit():
                        board.add_constraint(
                            Constraint(ConstraintType.VALUE, v, int(k))
                        )
                    elif len(k) >= 2 and k[1] in CONSTRAINT_TYPE_MAP:
                        val_str = "0" if k[1] in ("=", "!") else k[2:]
                        board.add_constraint(
                            Constraint(
                                CONSTRAINT_TYPE_MAP[k[1]],
                                v,
                                int(val_str) if val_str else 0,
                            )
                        )

                return board, dominoes
        except (FileNotFoundError, ValueError) as e:
            raise type(e)(f"Error reading CSV {filename}: {e}")


def get_puzzle_reader(filename: str) -> PipsPuzzleReader:
    """Factory function to return a puzzle reader based on file extension.

    Args:
        filename (str): The puzzle filename.

    Returns:
        PipsPuzzleReader: A reader instance (TomlPuzzleReader or CsvPuzzleReader).

    Raises:
        ValueError: If the file format is unsupported.
    """
    if filename.endswith(".toml"):
        return TomlPuzzleReader()
    if filename.endswith(".csv"):
        return CsvPuzzleReader()
    raise ValueError(f"Unsupported format: {filename}")


def read_toml(filename: str) -> tuple[Board, list[Domino]]:
    """Helper function to read a TOML puzzle file.

    Args:
        filename (str): Path to the TOML file.

    Returns:
        tuple[Board, list[Domino]]: Parsed board and dominoes.
    """
    return TomlPuzzleReader().read(filename)


def read_csv(filename: str) -> tuple[Board, list[Domino]]:
    """Helper function to read a CSV puzzle file.

    Args:
        filename (str): Path to the CSV file.

    Returns:
        tuple[Board, list[Domino]]: Parsed board and dominoes.
    """
    return CsvPuzzleReader().read(filename)
