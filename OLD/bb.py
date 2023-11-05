# Bitboard representation for an 8x8 checkers board
# We'll represent the board such that the least significant bit (rightmost bit) corresponds to the top-left square
# and the most significant bit (leftmost bit) corresponds to the bottom-right square.
# For the sake of simplicity, we'll assume that the game is played on a 4x8 board, with only the dark squares being used
# (which is a common representation since checkers is only played on one color of squares).
# This means we'll use a 32-bit integer for each player.

# Initialize the board
player1 = 0b0000000000000000000011111111  # Player 1 has the bottom 2 rows
player2 = 0b1111111100000000000000000000  # Player 2 has the top 2 rows
kings = 0b0000000000000000000000000000  # No kings at the start

# Masks for capturing and moving
LEFT_CAPTURE_MASK = 0b00000000000000000000000011111111
RIGHT_CAPTURE_MASK = 0b00000000000000000000111111110000
KING_ROW = 0b11111111000000000000000000000000  # The row where pieces become kings


# Utility functions
def get_bitboard_string(bitboard):
    return format(bitboard, "032b")


def print_board(player1, player2, kings):
    print("Current board:")
    for row in range(8):
        line = ""
        for col in range(4):
            i = row * 4 + col
            if (player1 >> i) & 1:
                if (kings >> i) & 1:
                    line += "B "
                else:
                    line += "b "
            elif (player2 >> i) & 1:
                if (kings >> i) & 1:
                    line += "W "
                else:
                    line += "w "
            else:
                line += ". "
        print(line)


print_board(player1, player2, kings)

# # Functions for moving and capturing
# def can_capture(player, opponent, kings, left=True):
#     # Check if there are any captures available for the current player
#     if left:
#         shift = 5  # Moving from right to left (from player 1's perspective)
#         capture_mask = LEFT_CAPTURE_MASK
#     else:
#         shift = 4  # Moving from left to right
#         capture_mask = RIGHT_CAPTURE_MASK

#     jumpers = player & ((~(player | opponent)) >> shift) & capture_mask
#     captures = ((opponent & capture_mask) >> shift) & jumpers
#     return captures


# def apply_move(player, opponent, kings, move_from, move_to, become_king=False):
#     # Apply a move (or capture)
#     player ^= (1 << move_from) | (1 << move_to)
#     if become_king:
#         kings |= 1 << move_to
#     opponent &= ~(1 << move_to)  # Remove the opponent's piece if it was captured
#     return player, opponent, kings


# # Main gameplay loop (simplified for demonstration purposes)
# def game_loop(player1, player2, kings):
#     turn = 0  # 0 for player 1's turn, 1 for player 2's turn
#     while True:
#         print_board(player1, player2, kings)
#         if turn == 0:
#             # Player 1's turn
#             print("Player 1's turn")
#             captures = can_capture(player1, player2, kings, left=True)
#             if captures:
#                 print("Captures available for Player 1:", get_bitboard_string(captures))
#             # TODO: Implement user input or AI move decision
#             # For the sake of example, let's say Player 1 moves from square 12 to 16
#             player1, player2, kings = apply_move(
#                 player1, player2, kings, 12, 16, become_king=((1 << 16) & KING_ROW) != 0
#             )

#             turn = 1  # Switch turn to Player 2
#         else:
#             # Player 2's turn
#             print("Player 2's turn")
#             captures = can_capture(player2, player1, kings, left=False)
#             if captures:
#                 print("Captures available for Player 2:", get_bitboard_string(captures))
#             # TODO: Implement user input or AI move decision
#             # For the sake of example, let's say Player 2 moves from square 1 to 5
#             player2, player1, kings = apply_move(
#                 player2, player1, kings, 1, 5, become_king=((1 << 5) & KING_ROW) != 0
#             )
#             turn = 0  # Switch turn back to Player 1
#         # TODO: Implement game over condition checks


# # Start the game
# game_loop(player1, player2, kings)
