import pathlib
import signal
import sys
import time

# Assuming checkers and heuristic modules are in the parent directory as in the first script
parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))

from checkers import *
from checkers import PlayerTurn, do_move, generate_legal_moves
from heuristic import smart as heuristic_function

global NC
NC = 0


class TimeOutException(Exception):
    pass


def signal_handler(signum, frame):
    raise TimeOutException()


def sort_moves_by_heuristic(legal_moves, position, current_player):
    if not legal_moves:
        return None

    if (
        len(legal_moves[0]) == 2
    ):  # jump moves are presorted by ascending sequence length.
        # if legal_moves[0] contains only two integers that means that there are only single jumps or only simple moves availible.
        WP, BP, K = position
        move_evaluations = [
            (
                move,
                heuristic_function(
                    *do_move(*position, move, current_player),
                    turn=current_player,
                    legal_moves=legal_moves,
                    depth=0,
                    global_board_state=(WP, BP, K),
                ),
            )
            for move in legal_moves
        ]
        move_evaluations.sort(  # sort the simple moves by heuristic function for higher probability of a/b prune
            key=lambda x: x[1], reverse=current_player == PlayerTurn.WHITE
        )
        sorted_moves = [move for move, _ in move_evaluations]
        return sorted_moves
    else:  # this branch implies that there is atleast one double jump move.
        return legal_moves  # in this case the legal moves are already presorted by len so there is no need to sort on heuristic.
        # will assume that multiple captures are a better indicator of a good move then the eval.


def minimax(
    position,
    depth,
    alpha,
    beta,
    current_player,
    current_depth=0,
    is_root=False,
    global_board_state=None,
):
    legal_moves = sort_moves_by_heuristic(
        generate_legal_moves(*position, current_player),
        position,
        current_player,
    )
    global NC
    NC += 1

    if depth == 0 or not legal_moves:
        return None, heuristic_function(
            *position,
            turn=current_player,
            legal_moves=legal_moves,
            depth=current_depth,
            global_board_state=global_board_state,
        )

    best_move = None
    if current_player == PlayerTurn.WHITE:  # MAXIMIZING PLAYER
        max_eval = float("-inf")
        for move in legal_moves:
            new_position = do_move(*position, move, current_player)
            _, eval = minimax(
                position=new_position,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
                current_player=PlayerTurn.BLACK,
                current_depth=(current_depth + 1),
                is_root=False,
                global_board_state=global_board_state,
            )
            if eval > max_eval:
                max_eval = eval
                best_move = move if is_root else None
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return best_move, max_eval
    else:  # MINIMIZING PLAYER
        min_eval = float("inf")
        for move in legal_moves:
            new_position = do_move(*position, move, current_player)
            _, eval = minimax(
                position=new_position,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
                current_player=PlayerTurn.WHITE,
                current_depth=(current_depth + 1),
                is_root=False,
                global_board_state=global_board_state,
            )
            if eval < min_eval:
                min_eval = eval
                best_move = move if is_root else None
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return best_move, min_eval


def AI(
    position,
    current_player,
    max_depth=9999,
    time_limit=5,
    heuristic=None,
    early_stop_depth=999,
    global_board_state=None,
):
    best_move = None
    best_score = float("-inf") if current_player == PlayerTurn.WHITE else float("inf")
    depth_reached = 0
    stable_depths = 0  # Track the number of depths where the best move hasn't changed
    last_best_move = None

    start_time = time.time()
    legal_moves = generate_legal_moves(*position, current_player)

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(time_limit)

    try:
        for depth in range(1, max_depth + 1):
            current_depth = 0  # Initialize currentDepth at the root level
            alpha = float("-inf")
            beta = float("inf")

            move, score = minimax(
                position=position,
                depth=depth,
                alpha=alpha,
                beta=beta,
                current_player=current_player,
                current_depth=current_depth,
                is_root=True,
                global_board_state=global_board_state,
            )

            # Debugging information
            # print(
            #     f"Depth: {depth}, Move: {move}, Score: {score}, Best Move: {best_move}, Best Score: {best_score}"
            # )

            if move is not None:
                if (
                    move != last_best_move or score != best_score
                ):  # Check if move or score has changed
                    best_move = move
                    best_score = score
                    stable_depths = 0  # Reset stability count
                    # print(
                    #     f"New best move found at depth {depth}. Resetting stable depths."
                    # )
                else:
                    stable_depths += 1  # Increment stability count
                    # print(
                    #     f"No change in best move/score at depth {depth}. Stable depths count: {stable_depths}"
                    # )

                if stable_depths >= early_stop_depth:
                    break  # Early stop if the best move hasn't changed for early_stop_depth depths

            depth_reached = depth
            last_best_move = best_move

            if time.time() - start_time >= time_limit:
                raise TimeOutException()

            # Update legal_moves for the next iteration
            legal_moves = generate_legal_moves(*position, current_player)

        signal.alarm(0)  # Cancel the alarm if we finished in time

    except TimeOutException:
        signal.alarm(0)  # Cancel the alarm since we've run out of time
        if best_move is None and legal_moves:
            best_move = legal_moves[0]  # Select the first legal move as a last resort

    print("Total nodes evaluated:", NC)
    print("Depth reached:", depth_reached)
    return best_move, depth_reached
