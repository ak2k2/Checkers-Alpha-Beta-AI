import time

import pygame

from checkers import *
from heuristic import *

# from minimax_alphabeta import *
from minimax_alphabeta import AI
from util.helpers import *

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800  # Window size
ROWS, COLS = 8, 8  # Number of rows and cols
SQUARE_SIZE = WIDTH // COLS


# Colors
# Convert hex colors to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


PLAYABLE_COLOR = hex_to_rgb("#D0AE8B")  # Unplayable squares
UNPLAYABLE_COLOR = hex_to_rgb("#976C40")  # Playable squares
WHITE = hex_to_rgb("#DEC5AB")
BLACK = hex_to_rgb("#180000")
HIGHLIGHT = (255, 255, 0)  # Yellow for highlighting selected piece


def draw_board(win):
    win.fill(UNPLAYABLE_COLOR)
    for row in range(ROWS):
        for col in range(row % 2, ROWS, 2):
            pygame.draw.rect(
                win,
                PLAYABLE_COLOR,
                (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            )


def draw_piece(win, row, col, color):
    pygame.draw.circle(
        win,
        color,
        (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
        SQUARE_SIZE // 2 - 10,
    )


def draw_king(win, row, col, color):
    points = [
        (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + 10),
        (col * SQUARE_SIZE + 10, row * SQUARE_SIZE + SQUARE_SIZE - 10),
        (col * SQUARE_SIZE + SQUARE_SIZE - 10, row * SQUARE_SIZE + SQUARE_SIZE - 10),
    ]
    pygame.draw.polygon(win, color, points)


def draw_pieces(win, WP, BP, K):
    for row in range(ROWS):
        for col in range(COLS):
            if row % 2 != col % 2:
                index = (7 - row) * 4 + (col // 2)
                is_king = K & (1 << index)
                if WP & (1 << index):
                    if is_king:
                        draw_king(win, row, col, WHITE)
                    else:
                        draw_piece(win, row, col, WHITE)
                elif BP & (1 << index):
                    if is_king:
                        draw_king(win, row, col, BLACK)
                    else:
                        draw_piece(win, row, col, BLACK)


def coordinates_to_bit(row, col):
    # Convert 2D board coordinates to a single-dimensional bit index
    # Adjust row index to start from the bottom
    adjusted_row = 7 - row
    bit_index = adjusted_row * 4 + col // 2
    return bit_index


def get_move_from_click(legal_moves, row, col):
    bit_index = coordinates_to_bit(row, col)
    for move in legal_moves:
        if move[0] == bit_index:
            return move
    return None


def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers AI")
    # mouse_button_down = False

    WP, BP, K = get_fresh_board()
    human_color = PlayerTurn.WHITE
    current_player = PlayerTurn.BLACK
    selected_piece = None
    legal_moves = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and current_player == human_color:
                pos = pygame.mouse.get_pos()
                row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE

                if row % 2 != col % 2:  # Click on a playable square
                    bit_index = coordinates_to_bit(row, col)

                    # Check if the clicked square contains a human player's piece
                    is_human_piece = (
                        (WP & (1 << bit_index))
                        if human_color == PlayerTurn.WHITE
                        else (BP & (1 << bit_index))
                    )

                    if is_human_piece:
                        # If a different piece is clicked, update the selected_piece
                        if selected_piece != bit_index:
                            selected_piece = bit_index
                            legal_moves = generate_legal_moves(
                                WP, BP, K, current_player
                            )
                            print(
                                f"Selected piece: {selected_piece}, row: {row}, col: {col}"
                            )
                        else:
                            # Deselect if the same piece is clicked again
                            selected_piece = None
                            print("Deselected the piece")
                    elif selected_piece is not None:
                        # A piece is already selected and a new square is clicked
                        destination = bit_index
                        print(f"Destination: {destination}, row: {row}, col: {col}")
                        if [selected_piece, destination] in legal_moves or (
                            selected_piece,
                            destination,
                        ) in legal_moves:
                            WP, BP, K = do_move(
                                WP, BP, K, (selected_piece, destination), current_player
                            )
                            current_player = switch_player(current_player)
                            selected_piece = None  # Reset selected piece after a move
                        else:
                            print("ILLEGAL move. Try again.")
                            selected_piece = (
                                None  # Reset selected piece if move is invalid
                            )

        draw_board(win)
        draw_pieces(win, WP, BP, K)

        # Highlight the selected piece
        if selected_piece is not None:
            # Convert bit index to Pygame board coordinates
            adjusted_row = 7 - (selected_piece // 4)
            col = (selected_piece % 4) * 2
            if adjusted_row % 2 == 0:
                col += 1

            pygame.draw.rect(
                win,
                HIGHLIGHT,
                (
                    col * SQUARE_SIZE,
                    adjusted_row * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                ),
                5,
            )

        pygame.display.update()

        # AI's turn
        if current_player != human_color:
            legal_moves = generate_legal_moves(WP, BP, K, current_player)
            if not legal_moves:
                print("YOU WON!")
                break
            if legal_moves:
                best_move = random.choice(legal_moves)
                WP, BP, K = do_move(WP, BP, K, best_move, current_player)
                current_player = switch_player(current_player)
            time.sleep(1)  # Simulate AI thinking

    pygame.quit()


if __name__ == "__main__":
    main()
