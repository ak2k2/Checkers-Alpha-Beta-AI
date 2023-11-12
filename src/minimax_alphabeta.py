import signal
import time

from checkers import *
from checkers import PlayerTurn, do_move, generate_legal_moves
from heuristic import (
    new_heuristic,
    old_heuristic,
)

global NC
NC = 0


class TimeOutException(Exception):
    pass


def signal_handler(signum, frame):
    raise TimeOutException()


def sort_moves_by_heuristic(legal_moves, position, current_player, heuristic):
    if not legal_moves:
        return []
    if heuristic == "new_heuristic":
        heuristic_function = new_heuristic
    elif heuristic == "old_heuristic":
        heuristic_function = old_heuristic
    else:
        raise ValueError("Invalid heuristic function specified")

    move_evaluations = [
        (
            move,
            heuristic_function(
                *do_move(*position, move, current_player), current_player
            ),
        )
        for move in legal_moves
    ]

    move_evaluations.sort(
        key=lambda x: x[1], reverse=current_player == PlayerTurn.WHITE
    )
    sorted_moves = [move for move, _ in move_evaluations]
    return sorted_moves


def minimax(position, depth, alpha, beta, current_player, heuristic="new_heuristic"):
    legal_moves = generate_legal_moves(*position, current_player)

    # Check if the game has ended (either by reaching a terminal state or by reaching the maximum depth)
    if (
        depth == 0 or not legal_moves
    ):  # If at max depth or no legal moves, then it's a terminal state or a leaf node
        global NC
        NC += 1
        if not legal_moves:
            # If there are no legal moves, then this player has lost
            return float("-inf") if current_player == PlayerTurn.WHITE else float("inf")
        else:
            # Here we reach the maximum depth, so we evaluate the position using the heuristic function
            if heuristic == "new_heuristic":
                return new_heuristic(*position, current_player)
            elif heuristic == "old_heuristic":
                return old_heuristic(*position)

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


def AI(position, current_player, max_depth, time_limit=5, heuristic="new_heuristic"):
    best_move = None
    best_score = float("-inf") if current_player == PlayerTurn.WHITE else float("inf")
    depth_reached = 0
    start_time = time.time()

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(time_limit)

    try:
        for depth in range(1, max_depth + 1):
            alpha = float("-inf")
            beta = float("inf")

            legal_moves = (
                sort_moves_by_heuristic(  # Generate legal moves sorted by heuristic
                    generate_legal_moves(*position, current_player),
                    position,
                    current_player,
                    heuristic,
                )
            )

            if not legal_moves:
                # No legal moves available, return immediately indicating game is lost
                return None, depth

            for move in legal_moves:
                if time.time() - start_time >= time_limit:
                    raise TimeOutException()

                new_position = do_move(*position, move, current_player)
                score = minimax(
                    new_position,
                    depth - 1,
                    alpha,
                    beta,
                    switch_player(current_player),
                    heuristic,
                )

                if current_player == PlayerTurn.WHITE:
                    if score > best_score:
                        best_score = score
                        best_move = move
                    alpha = max(alpha, score)
                else:
                    if score < best_score:
                        best_score = score
                        best_move = move
                    beta = min(beta, score)

                if beta <= alpha:
                    break

            depth_reached = depth

        signal.alarm(0)  # Cancel the alarm if we finished in time

    except TimeOutException:
        signal.alarm(0)  # Cancel the alarm since we've run out of time
        # If a timeout occurs but we don't have a best move, we select any legal move.
        if best_move is None and legal_moves:
            best_move = legal_moves[0]  # Select the first legal move as a last resort
    print("Total nodes evaluated:", NC)
    return best_move, depth_reached
