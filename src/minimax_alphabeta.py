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
