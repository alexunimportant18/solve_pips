import copy
import functools
import logging
import math
from functools import lru_cache
from itertools import combinations_with_replacement, permutations

from board import Board, color_sequence
from constraint import ConstraintType
from direction import Direction
from domino import Domino, reverse_domino

# Memoization cache to store failed board states, it can save up to 33% time
cache_stats = {"failed_states": set(), "call_saved": 0, "call_total": 0}


def solve(
    board: Board, available_dominoes: set[Domino]
) -> tuple[Board, set[Domino]] | None:
    """Recursively tries to place dominoes on the board to find a valid solution.

    This function implements a backtracking algorithm. It finds the next empty cell,
    tries to place each available domino in each possible orientation and direction,
    and then recursively calls itself. If a path leads to a dead end, it backtracks
    and tries another option.

    Args:
        board (Board): The game board instance.
        available_dominoes (set[Domino]): The set of dominoes still available for placement.

    Returns:
        tuple[Board, set[Domino]] | None: A tuple of the solved Board and remaining
            dominoes if a solution is found; otherwise None.
    """
    # Base case: If there are no dominoes left to place, we have found a solution.
    if not available_dominoes:
        print("\nSolution found!")
        return board, available_dominoes

    # Increment total function calls every time solve() is called
    state_key = None

    cache_stats["call_total"] += 1

    # Create a hashable key for the current board state and available dominoes
    board_tuple = tuple(tuple(row) for row in board.board)
    dominoes_tuple = tuple(sorted(available_dominoes))
    state_key = (board_tuple, dominoes_tuple)

    # If we've already tried this state and it failed, return immediately
    if state_key in cache_stats["failed_states"]:
        cache_stats["call_saved"] += 1
        return None

    # Find the next empty cell to fill. If the board is full but we still have
    # dominoes, this path is invalid.
    position = board.find_next_empty_cell()
    if position is None:
        return None

    # Iterate through all dominoes that could possibly be placed at the current empty cell.
    for candidate_domino in available_dominoes:
        domino_to_remove = None
        if (
            candidate_domino in board.possible_dominoes[position.row][position.col]
            #            or reverse_domino(candidate_domino)#
            #            in board.possible_dominoes[position.row][position.col]
        ):
            domino_to_remove = candidate_domino
        else:
            continue

        # We have the domino. Now try to place it in all valid orientations and directions.
        domino_list = (
            [candidate_domino]
            if candidate_domino.left == candidate_domino.right
            else [candidate_domino, reverse_domino(candidate_domino)]
        )
        for placement_orientation in domino_list:
            for direction in Direction:
                # Save the current state we need to restore after recursion
                row1, col1 = position.row, position.col
                row2, col2 = position.row, position.col
                if direction == Direction.NORTH:
                    row2 -= 1
                elif direction == Direction.EAST:
                    col2 += 1
                elif direction == Direction.SOUTH:
                    row2 += 1
                elif direction == Direction.WEST:
                    col2 -= 1

                # Validate positions are within bounds before attempting to place
                if not (0 <= row2 < board.n_row and 0 <= col2 < board.n_col):
                    continue
                if (
                    board.board[row1][col1] is not None
                    or board.board[row2][col2] is not None
                ):
                    continue

                # Save the original values so we can restore them after recursion
                orig_board1 = board.board[row1][col1]
                orig_board2 = board.board[row2][col2]
                orig_color1 = board.cell_colors[row1][col1]
                orig_color2 = board.cell_colors[row2][col2]
                orig_color_index = board.color_index

                # Try to place the domino.
                if board.place_domino(
                    placement_orientation, position, direction, list(available_dominoes)
                ):
                    remaining_dominoes = set(available_dominoes)
                    remaining_dominoes.remove(domino_to_remove)

                    # Recurse with the same board instance (we'll backtrack later)
                    result = solve(board, remaining_dominoes)

                    if result is not None:
                        return result

                # Always undo the changes to the board
                board.board[row1][col1] = orig_board1
                board.board[row2][col2] = orig_board2
                board.cell_colors[row1][col1] = orig_color1
                board.cell_colors[row2][col2] = orig_color2
                board.color_index = orig_color_index

    cache_stats["failed_states"].add(state_key)
    return None
