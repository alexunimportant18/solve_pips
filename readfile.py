import csv
import tomllib

from board import Board
from constraint import Constraint, ConstraintType
from domino import Domino
from position import Position

constraint_type_map = {
    "<": ConstraintType.LT,
    ">": ConstraintType.GT,
    "+": ConstraintType.TOTAL,
    "=": ConstraintType.EQUAL,
    "!": ConstraintType.NE,
}


def read_toml(filename: str) -> tuple[Board, list[Domino]]:
    # if any error, let it raise exception and propagate up
    with open(filename, "rb") as f:
        config = tomllib.load(f)

    # print(config)

    lines = config["board"]["layout"]
    height = len(lines)
    width = len(lines[0])
    board = Board(width=width, height=height)

    cells = []
    for line in lines:
        cells.append(list(line))

    # print(cells)

    constraints = config["constraints"]
    # constraints_list = []

    for k, v in constraints.items():
        constraint_type = constraint_type_map[v[0]]
        value = 0 if v[0] == "=" or v[0] == "!" else v[1:]
        position_list = []
        for i, row in enumerate(cells):
            for j, cell in enumerate(row):
                # print(f"i, j: ({i}, {j}), cell: {cell}, value: {value}")
                if cell == k:
                    position_list.append(Position(row=i, col=j))
        constraint = Constraint(constraint_type, position_list, int(value))
        board.add_constraint(constraint)

    # handle DEAD cells
    position_list = []
    for i, row in enumerate(cells):
        for j, cell in enumerate(row):
            if cell == "x":
                position_list.append(Position(row=i, col=j))
                constraint = Constraint(ConstraintType.DEAD, position_list, -1)
                board.add_constraint(constraint)

    # handle FREE cells

    position_list = []
    for i, row in enumerate(cells):
        for j, cell in enumerate(row):
            if cell == ".":
                position_list.append(Position(row=i, col=j))
                constraint = Constraint(ConstraintType.FREE, position_list, None)
                board.add_constraint(constraint)

    # handle VALUE cells

    position_list = []
    for i, row in enumerate(cells):
        for j, cell in enumerate(row):
            if cell.isdigit():
                position_list.append(Position(row=i, col=j))
                constraint = Constraint(ConstraintType.VALUE, position_list, int(cell))
                board.add_constraint(constraint)

    dominoes = set()
    for v in config["dominoes"]["tiles"]:
        # print(v)
        dominoes.add(Domino(int(v[0]), int(v[1])))

    return board, list(dominoes)


def read_csv(filename: str) -> tuple[Board, list[Domino]]:
    # if any error, let it raise exception and propagate up as the script cannot continue
    dominoes = []

    dict = {}
    with open(filename, mode="r") as file:
        file = csv.reader(file)
        width, height = 0, 0
        for i, line in enumerate(file):
            if i == 0:
                for cell in line:
                    cell = cell.strip()
                    dominoes.append(Domino(int(cell[0]), int(cell[1])))
            else:
                row = i - 1
                for col, cell in enumerate(line):
                    cell = cell.strip()
                    width = max(width, col + 1)
                    height = max(height, row + 1)
                    if cell in dict:
                        dict[cell].append(Position(row=row, col=col))
                    else:
                        dict[cell] = [Position(row=row, col=col)]

    board = Board(width=width, height=height)
    for k, v in dict.items():
        if k == ".":
            constraint = Constraint(ConstraintType.FREE, v, None)
            board.add_constraint(constraint)
            continue

        if k == "x":
            constraint = Constraint(ConstraintType.DEAD, v, -1)
            board.add_constraint(constraint)
            continue

        if k.isdigit():
            constraint = Constraint(ConstraintType.VALUE, v, int(k))
            board.add_constraint(constraint)
            continue

        spec = k[1:]
        # print(spec)
        constraint_type = constraint_type_map[spec[0]]
        value = 0 if spec[0] == "=" or spec[0] == "!" else spec[1:]
        constraint = Constraint(constraint_type, v, int(value))
        board.add_constraint(constraint)

    # print(dominoes)
    # board.print_constraints()

    return board, dominoes
