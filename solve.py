import copy
import functools
import logging
import math
from itertools import combinations_with_replacement, permutations

from board import Board
from constraint import ConstraintType
from direction import Direction
from domino import Domino, reverse_domino


def solve(
    board: Board, available_dominoes: set[Domino]
) -> tuple[Board, set[Domino]] | None:
    """
    Recursively tries to place dominoes on the board to find a valid solution.

    This function implements a backtracking algorithm. It finds the next empty cell,
    tries to place each available domino in each possible orientation and direction,
    and then recursively calls itself. If a path leads to a dead end, it backtracks
    and tries another option.
    """
    # Base case: If there are no dominoes left to place, we have found a solution.
    if not available_dominoes:
        print("Solution found!")
        return board, available_dominoes

    # Find the next empty cell to fill. If the board is full but we still have
    # dominoes, this path is invalid.
    position = board.find_next_empty_cell()
    # print(f"  next empty cell: {position}")
    if position is None:
        return None

    # print(
    #    f"Trying to place a domino at {position}. {len(available_dominoes)} dominoes left."
    # )
    # print(
    #    f"Possible dominoes for this cell: {board.possible_dominoes[position.row][position.col]}"
    # )

    # Iterate through all dominoes that could possibly be placed at the current empty cell.
    # This list is pre-calculated to satisfy local constraints, pruning the search.
    # print(f"  available dominoes: {available_dominoes}")
    for candidate_domino in available_dominoes:
        # print(f"  Checking candidate domino: {candidate_domino}")
        # Determine if we have this domino in our hand (in either orientation).
        domino_to_remove = None
        if (
            candidate_domino in board.possible_dominoes[position.row][position.col]
            or reverse_domino(candidate_domino)
            in board.possible_dominoes[position.row][position.col]
        ):
            # print(f"    {candidate_domino} is a valid candidate!")
            domino_to_remove = candidate_domino
        else:
            # If we don't have this domino, we can't place it. Continue to the next candidate.
            # print(f"    {candidate_domino} is not a valid candidate, skipping.")
            continue

        # We have the domino. Now try to place it in all valid orientations and directions.
        # Using a set for orientations handles symmetric dominoes (e.g., (3,3)) correctly.
        domino_list = (
            [candidate_domino]
            if candidate_domino.left == candidate_domino.right
            else [candidate_domino, reverse_domino(candidate_domino)]
        )
        for placement_orientation in domino_list:
            # print(f"    Trying {domino_list}")
            # print(f"    Trying placement orientation: {placement_orientation}")
            for direction in Direction:
                # print(f"      Trying direction: {direction}")
                # Create a fresh copy of the board for this attempt.
                # This is the crucial fix to prevent state corruption between attempts.
                board_copy = copy.deepcopy(board)

                # Try to place the domino.
                if board_copy.place_domino(placement_orientation, position, direction):
                    # print(
                    #    f"  Placed {placement_orientation} at {position} going {direction}.  Board becomes\n{board_copy}"
                    # )
                    # If placement is successful, create the new set of remaining dominoes.
                    remaining_dominoes = available_dominoes.copy()
                    remaining_dominoes.remove(domino_to_remove)

                    # Recurse with the new state.
                    result = solve(board_copy, remaining_dominoes)

                    # If the recursive call found a complete solution, propagate it up.
                    if result is not None:
                        return result

    # If we've tried all possible dominoes and placements for this cell and none led to a solution,
    # then this path is a dead end. Backtrack by returning None.
    # print(f"Backtracking from {position}. No valid placement found.")
    return None
