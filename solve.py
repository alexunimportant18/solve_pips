from board import Board
from domino import Domino
from constraint import ConstraintType
from direction import Direction
import copy
import logging
from itertools import permutations
import math
import functools
from itertools import combinations_with_replacement

def solve(board: Board, dominoes: set[Domino]) -> tuple[Board, set[Domino]] | None:
    """
    Recursively tries to place dominoes on the board to find a valid solution.

    This function implements a backtracking algorithm. It finds the next empty cell,
    tries to place each available domino in each possible orientation and direction,
    and then recursively calls itself. If a path leads to a dead end, it backtracks
    and tries another option.
    """
    # Base case: If there are no dominoes left to place, we have found a solution.
    if not dominoes:
        return board, dominoes

    # Find the next empty cell to fill. If the board is full but we still have
    # dominoes, this path is invalid.
    position = board.find_next_empty_cell()
    if position is None:
        return None

    # Iterate through all dominoes that could possibly be placed at the current empty cell.
    # This list is pre-calculated to satisfy local constraints, pruning the search.
    for candidate_domino in board.possible_dominoes[position[0]][position[1]]:
        
        # Determine if we have this domino in our hand (in either orientation).
        domino_to_remove = None
        if candidate_domino in dominoes:
            domino_to_remove = candidate_domino
        #elif candidate_domino.reversed() in dominoes:
        #    domino_to_remove = candidate_domino.reversed()
        
        if domino_to_remove is None:
            # If we don't have this domino, we can't place it. Continue to the next candidate.
            continue

        # We have the domino. Now try to place it in all valid orientations and directions.
        # Using a set for orientations handles symmetric dominoes (e.g., (3,3)) correctly.
        for placement_orientation in [candidate_domino, candidate_domino.reversed()]:
            for direction in Direction:
                # Create a fresh copy of the board for this attempt.
                # This is the crucial fix to prevent state corruption between attempts.
                board_copy = copy.deepcopy(board)

                # Try to place the domino.
                if board_copy.place_domino(placement_orientation, position, direction):
                    # If placement is successful, create the new set of remaining dominoes.
                    remaining_dominoes = dominoes.copy()
                    remaining_dominoes.remove(domino_to_remove)
                    
                    # Recurse with the new state.
                    result = solve(board_copy, remaining_dominoes)
                    
                    # If the recursive call found a complete solution, propagate it up.
                    if result is not None:
                        return result

    # If we've tried all possible dominoes and placements for this cell and none led to a solution,
    # then this path is a dead end. Backtrack by returning None.
    return None