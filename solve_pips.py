from board import Board
from constraint import Constraint, ConstraintType
from domino import Domino
from solve import solve
from readfile import read_toml, read_csv
from options import Options
import logging

logging.basicConfig(level=logging.INFO)

def gen_today_data() -> tuple[Board, list[Domino]]:
    board = Board(width=5, height=4)
    board.add_constraint(Constraint(ConstraintType.FREE, positions=[(0, 0), (2, 2)], value=12))
    board.add_constraint(Constraint(ConstraintType.TOTAL, positions=[(0, 1), (1, 1)], value=6))
    board.add_constraint(Constraint(ConstraintType.EQUAL, positions=[(0, 2), (1, 2)], value=0))
    board.add_constraint(Constraint(ConstraintType.TOTAL, positions=[(0, 3), (0, 4)], value=8))

    board.add_constraint(Constraint(ConstraintType.DEAD, positions=[(1, 0), (2, 0), (3, 0), (1, 3), (3, 3), (3, 4)])) 

    board.add_constraint(Constraint(ConstraintType.TOTAL, positions=[(1, 4), (2, 3), (2, 4)], value=4))
    board.add_constraint(Constraint(ConstraintType.EQUAL, positions=[(2, 1), (3, 1), (3, 2)]))
        
    dominoes = { 
        Domino(0, 3),
        Domino(2, 2),
        Domino(0, 4),
        Domino(4, 6),
        Domino(5, 5),
        Domino(3, 6),
        Domino(0, 5)
    }

    return board, dominoes

def gen_test_data() -> tuple[Board, list[Domino]]:
    board = Board(width=4, height=4)
    board.add_constraint(Constraint(ConstraintType.TOTAL, positions=[(0, 0), (0, 1)], value=12))
    board.add_constraint(Constraint(ConstraintType.FREE, positions=[(0, 2)]))
    board.add_constraint(Constraint(ConstraintType.TOTAL, positions=[(0, 3)], value=0))
    board.add_constraint(Constraint(ConstraintType.TOTAL, positions=[(1, 0), (1, 1), (1, 2), (1, 3)], value=7))
    board.add_constraint(Constraint(ConstraintType.TOTAL, positions=[(2, 0), (2, 1)], value=11)) 
    board.add_constraint(Constraint(ConstraintType.DEAD, positions=[(2, 2), (2, 3)])) 
    board.add_constraint(Constraint(ConstraintType.TOTAL, positions=[(3, 0), (3, 1)], value=4)) 
    board.add_constraint(Constraint(ConstraintType.TOTAL, positions=[(3, 2)], value=1)) 
    board.add_constraint(Constraint(ConstraintType.FREE, positions=[(3, 3)], value=0))

    #board.print_constraints()
    dominoes = { 
        Domino(2, 6),
        Domino(1, 6),
        Domino(2, 2),
        Domino(0, 2),
        Domino(1, 5),
        Domino(3, 6),
        Domino(1, 2)
    }

    return board, dominoes

def main():
    opt: Namespace = Options().getparse()
    if opt.verbose:
        logging.basicConfig(
            format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d:%H:%M:%S",
            level=logging.INFO,
        )
    else:
        logging.basicConfig(
            format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d:%H:%M:%S",
            level=logging.ERROR,
        )
    
    if opt.toml_file:
        board, dominoes = read_toml(opt.toml_file)
    
    if opt.csv_file:
        board, dominoes = read_csv(opt.csv_file)

    #board, dominoes = gen_real_data()

    print(f"{dominoes=}")
    print("Board =")
    board.print_constraints()
    #print(find_possible_dominoes_with_total_count(dominoes, 1, 1))
    
    board.generate_possible_dominoes(dominoes)
    #logging.debug(f"sorted positions: {board.sorted_positions}")
    #board.print_possible_dominoes()

    result = solve(board, dominoes)
    if result:
        answer, _ = result
        print("\nAnswer =")
        answer.print_board()

if __name__ == "__main__":
    main()
