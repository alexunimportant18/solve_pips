import logging
from argparse import Namespace

from board import Board
from constraint import Constraint, ConstraintType
from domino import Domino
from options import Options
from readfile import read_csv, read_toml
from solve import cache_stats, solve

logging.basicConfig(level=logging.INFO)


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

    board = None
    dominoes = []

    if opt.toml_file:
        board, dominoes = read_toml(opt.toml_file)

    if opt.csv_file:
        board, dominoes = read_csv(opt.csv_file)

    if not opt.toml_file and not opt.csv_file:
        raise ValueError("Either toml_file or csv_file must be provided")

    # board, dominoes = gen_real_data()

    if dominoes and board:
        print(f"{dominoes=}")
        print("Board =")
        board.print_constraints()
        # print(find_possible_dominoes_with_total_count(dominoes, 1, 1))

        board.generate_possible_dominoes(set(dominoes))
        # logging.debug(f"sorted positions: {board.sorted_positions}")
        # board.print_possible_dominoes()

        result = solve(board, set(dominoes))
        if result:
            answer, _ = result
            print("\nAnswer =")
            answer.print_board()
        else:
            print("No solution found")

        # Print cache/memoization statistics
        hit_rate = (
            cache_stats["call_saved"]
            * 100
            / (cache_stats["call_total"] + cache_stats["call_saved"])
        )
        print("\nCache statistics:")
        print(f"  Total function calls: {cache_stats['call_total']}")
        # print(f"  Total failed states tracked: {len(cache_stats['failed_states'])}")
        print(f"  Function calls cached: {cache_stats['call_saved']} ({hit_rate:.2f}%)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        exit(1)
