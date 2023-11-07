from main import generate_legal_moves
from heuristic import basic_heuristic
from game import do_move, PlayerTurn


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


def AI(position, max_depth):
    """
    Apply minimax with alpha-beta pruning via iterative deepening.
    """
    best_move = None
    best_score = float("-inf")
    for depth in range(1, max_depth + 1):
        alpha = float("-inf")
        beta = float("inf")
        legal_moves = generate_legal_moves(*position, PlayerTurn.WHITE)
        for move in legal_moves:
            new_position = do_move(*position, move, PlayerTurn.WHITE)
            score = minimax(new_position, depth - 1, alpha, beta, PlayerTurn.BLACK)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)
    return best_move
