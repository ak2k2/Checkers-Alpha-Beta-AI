import pathlib
import signal
import sys
import time

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))

from checkers import *
from checkers import PlayerTurn, do_move, generate_legal_moves
from heuristic import evolve_base_B, new_heuristic, old_heuristic

global NC
NC = 0


class TimeOutException(Exception):
    pass


def sort_moves_by_heuristic(legal_moves, position, current_player, heuristic):
    if not legal_moves or legal_moves == []:
        return None
    if isinstance(heuristic, str):
        if heuristic == "new_heuristic":
            heuristic_function = new_heuristic
        elif heuristic == "old_heuristic":
            heuristic_function = old_heuristic
        elif heuristic == "evolve_base_B":
            heuristic_function = evolve_base_B
        else:
            raise ValueError("Invalid heuristic function specified")

        move_evaluations = [
            (
                move,
                heuristic_function(
                    *do_move(*position, move, current_player),
                    turn=current_player,
                    num_moves=len(legal_moves),
                ),
            )
            for move in legal_moves
        ]

    elif callable(heuristic):
        # Directly use the callable heuristic function for tuning
        move_evaluations = [
            (move, heuristic(*do_move(*position, move, current_player), current_player))
            for move in legal_moves
        ]

    else:
        raise ValueError("Invalid heuristic function specified")

    move_evaluations.sort(
        key=lambda x: x[1], reverse=current_player == PlayerTurn.WHITE
    )
    sorted_moves = [move for move, _ in move_evaluations]
    return sorted_moves


def minimax(position, depth, alpha, beta, current_player, heuristic="evolve_base_B"):
    legal_moves = generate_legal_moves(*position, current_player)

    # Check if the game has ended (either by reaching a terminal state or by reaching the maximum depth)
    if (
        depth == 0 or not legal_moves
    ):  # If at max depth or no legal moves, then it's a terminal state or a leaf node
        global NC
        NC += 1
        if not legal_moves:  # no legal moves for current player
            # return float("-inf") if current_player == PlayerTurn.WHITE else float("inf")
            if current_player == PlayerTurn.WHITE:
                return -1 * (
                    1_000_000 - (depth * 1_000)
                )  # Loose as slowly as possible and win as quickly as possible
            else:
                return 1_000_000 - (depth * 1_000)
        else:
            if isinstance(heuristic, str):
                # Here we reach the maximum depth, so we evaluate the position using the heuristic function
                if heuristic == "new_heuristic":
                    return new_heuristic(*position, turn=current_player)
                elif heuristic == "old_heuristic":
                    return old_heuristic(*position, turn=current_player)
                elif heuristic == "evolve_base_B":
                    return evolve_base_B(
                        *position,
                        turn=current_player,
                        num_moves=len(legal_moves),
                    )
                else:
                    raise ValueError("Invalid heuristic function specified")
            elif callable(heuristic):
                # Directly use the callable heuristic function
                return heuristic(*position, turn=current_player)

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


def threadsafe_AI(
    position,
    current_player,
    max_depth,
    time_limit=5,
    heuristic="evolve_base_B",
    early_stop_depth=100,  # Stop if no improvement for 'early_stop_depth' consecutive depths
):
    best_move = None
    best_score = float("-inf") if current_player == PlayerTurn.WHITE else float("inf")
    depth_reached = 0
    start_time = time.time()

    score_at_depth = {}  # Track the best score at each depth
    depth_without_improvement = 0  # Track depth levels without score improvement

    try:
        for depth in range(1, max_depth + 1):
            alpha = float("-inf")
            beta = float("inf")

            legal_moves = sort_moves_by_heuristic(
                generate_legal_moves(*position, current_player),
                position,
                current_player,
                heuristic,
            )

            if not legal_moves or legal_moves == []:
                return None, depth

            is_improved = False  # Flag to check if this depth provides a better score
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

                if (current_player == PlayerTurn.WHITE and score > best_score) or (
                    current_player != PlayerTurn.WHITE and score < best_score
                ):
                    best_score = score
                    best_move = move
                    is_improved = True

                if current_player == PlayerTurn.WHITE:
                    alpha = max(alpha, score)
                else:
                    beta = min(beta, score)

                if beta <= alpha:
                    break

            score_at_depth[depth] = best_score
            if is_improved:
                depth_without_improvement = 0  # Reset counter if score improved
            else:
                depth_without_improvement += 1  # Increment counter

            if depth_without_improvement >= early_stop_depth:
                # Stop if no improvement for 'early_stop_depth' consecutive depths
                break

            depth_reached = depth

    except TimeOutException:
        # If a timeout occurs but we don't have a best move, select any legal move.
        if best_move is None and legal_moves:
            best_move = legal_moves[0]

    return best_move, depth_reached
