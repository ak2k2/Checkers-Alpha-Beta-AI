import time
import signal

from checkers import *
from checkers import PlayerTurn, do_move, generate_legal_moves
from heuristic import basic_heuristic


class TimeOutException(Exception):
    pass


def signal_handler(signum, frame):
    raise TimeOutException("AI computation timed out")


def minimax(position, depth, alpha, beta, current_player):
    legal_moves = generate_legal_moves(*position, current_player)

    if (
        depth == 0 or not legal_moves
    ):  # If we are at max depth or there are no legal moves, game is over
        return basic_heuristic(*position)

    if current_player == PlayerTurn.WHITE:
        max_eval = float("-inf")
        for move in legal_moves:
            new_position = do_move(*position, move, current_player)
            eval = minimax(new_position, depth - 1, alpha, beta, PlayerTurn.BLACK)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for move in legal_moves:
            new_position = do_move(*position, move, current_player)
            eval = minimax(new_position, depth - 1, alpha, beta, PlayerTurn.WHITE)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


import time


def AI(position, max_depth, time_limit=5):
    """
    Apply minimax with alpha-beta pruning via iterative deepening with a time limit per move.
    """
    best_move = None
    best_score = float("-inf")
    start_time = time.time()

    for depth in range(1, max_depth + 1):
        alpha = float("-inf")
        beta = float("inf")
        legal_moves = generate_legal_moves(*position, PlayerTurn.WHITE)
        if not legal_moves:
            return None
        for move in legal_moves:
            # Check if time limit exceeded
            if time.time() - start_time >= time_limit:
                # If time limit exceeded, return the best move from the last full depth searched
                return best_move if best_move is not None else move

            new_position = do_move(*position, move, PlayerTurn.WHITE)
            score = minimax(new_position, depth - 1, alpha, beta, PlayerTurn.BLACK)

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)
            if beta <= alpha:
                break

        # If we have a result from the full depth search, we update the best move/score
        # Otherwise, the search was cut off by the time limit, and we use the best from the last full depth

    return best_move
