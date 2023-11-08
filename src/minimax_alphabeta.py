import time
import signal

from checkers import *
from checkers import PlayerTurn, do_move, generate_legal_moves
from heuristic import basic_heuristic, new_heuristic, basic_heuristic_2


class TimeOutException(Exception):
    pass


def signal_handler(signum, frame):
    raise TimeOutException("AI computation timed out")


def minimax(position, depth, alpha, beta, current_player, heuristic="basic_heuristic"):
    legal_moves = generate_legal_moves(*position, current_player)

    # Check if the game has ended (either by reaching a terminal state or by reaching the maximum depth)
    if (
        depth == 0 or not legal_moves
    ):  # If at max depth or no legal moves, then it's a terminal state or a leaf node
        if not legal_moves:
            # If there are no legal moves, then this player has lost
            print("A terminal state has been reached")
            return float("-inf") if current_player == PlayerTurn.WHITE else float("inf")
        else:
            # Here we reach the maximum depth, so we evaluate the position using the heuristic function
            if heuristic == "basic_heuristic":
                return basic_heuristic(*position)
            elif heuristic == "new_heuristic":
                return new_heuristic(*position)

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


def AI(position, current_player, max_depth, time_limit=5, heuristic="basic_heuristic"):
    best_move = None
    best_score = float("-inf") if current_player == PlayerTurn.WHITE else float("inf")
    depth_reached = 0  # Initialize depth reached
    start_time = time.time()

    # Set the signal alarm
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(time_limit)

    try:
        for depth in range(1, max_depth + 1):
            alpha = float("-inf")
            beta = float("inf")
            legal_moves = generate_legal_moves(*position, current_player)

            if not legal_moves:
                raise (None, depth)

            for move in legal_moves:
                new_position = do_move(*position, move, current_player)
                score = minimax(
                    new_position,
                    depth - 1,
                    alpha,
                    beta,
                    PlayerTurn.BLACK
                    if current_player == PlayerTurn.WHITE
                    else PlayerTurn.WHITE,
                    heuristic,  # Pass the heuristic function
                )

                if current_player == PlayerTurn.WHITE and score > best_score:
                    best_score = score
                    best_move = move
                elif current_player == PlayerTurn.BLACK and score < best_score:
                    best_score = score
                    best_move = move

                if current_player == PlayerTurn.WHITE:
                    alpha = max(alpha, score)
                else:
                    beta = min(beta, score)

                if beta <= alpha:
                    break

                # Check time constraint
                if time.time() - start_time >= time_limit:
                    raise TimeOutException()

            depth_reached = depth  # Update the depth reached

        signal.alarm(0)  # Cancel the alarm if we finished in time
    except TimeOutException:
        signal.alarm(0)  # Cancel the alarm since we've run out of time
        if best_move is None and legal_moves:
            best_move = legal_moves[
                0
            ]  # Choose any move if none was selected. This should not happen.

    return best_move, depth_reached
