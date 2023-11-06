def heuristic(WP, BP, WK, BK):
    # Basic weights
    piece_weight = 100
    king_weight = 175
    defended_piece_weight = 10

    # Count white and black pieces
    white_pieces = count_bits(WP)
    black_pieces = count_bits(BP)

    # Count white and black kings
    white_kings = count_bits(WK)
    black_kings = count_bits(BK)

    # Calculate defended pieces (this is a simplification)
    # For a real game, you'd also want to check if a piece is defended by another.
    white_defended = count_defended_pieces(WP, WK)
    black_defended = count_defended_pieces(BP, BK)

    # Evaluate the board state
    white_score = (
        white_pieces * piece_weight
        + white_kings * king_weight
        + white_defended * defended_piece_weight
    )
    black_score = (
        black_pieces * piece_weight
        + black_kings * king_weight
        + black_defended * defended_piece_weight
    )

    # Return the score from white's perspective
    return white_score - black_score


def count_bits(bitboard):
    # Count the number of set bits (pieces)
    count = 0
    while bitboard:
        count += 1
        bitboard &= bitboard - 1
    return count


# def count_defended_pieces(P, K):
#     # For simplicity, count pieces on the back row as defended.
#     back_row = 0xF0000000 if P == WP else 0x0000000F
#     defended_pieces = P & back_row
#     return count_bits(defended_pieces)


# def minimax(position, depth, alpha, beta, maximizingPlayer):
#     if depth == 0 or game_over(position):
#         return evaluate(position)

#     if maximizingPlayer:
#         maxEval = float("-inf")
#         for move in get_legal_moves(position):
#             eval = minimax(apply_move(position, move), depth - 1, alpha, beta, False)
#             maxEval = max(maxEval, eval)
#             alpha = max(alpha, eval)
#             if beta <= alpha:
#                 break
#         return maxEval
#     else:
#         minEval = float("inf")
#         for move in get_legal_moves(position):
#             eval = minimax(apply_move(position, move), depth - 1, alpha, beta, True)
#             minEval = min(minEval, eval)
#             beta = min(beta, eval)
#             if beta <= alpha:
#                 break
#         return minEval
