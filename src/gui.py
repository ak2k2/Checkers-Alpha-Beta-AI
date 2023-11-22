import pygame
import time

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


def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers AI")

    WP, BP, K = get_fresh_board()  # Get the initial board state
    K = insert_piece_by_pdntext(K, "A3")
    human_color = PlayerTurn.WHITE
    current_player = PlayerTurn.BLACK

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_board(win)
        draw_pieces(win, WP, BP, K)
        pygame.display.update()

        if current_player == human_color:  # Human's turn
            legal_moves = generate_legal_moves(WP, BP, K, current_player)
            if not legal_moves:  # Human lost
                print("YOU LOOSE!")
                break
            else:
                # Human's turn
                # print("Choose your move by index: ")
                # user_input = input("-> ")
                # try:
                #     selected_move_index = int(user_input)
                #     if selected_move_index not in range(len(legal_moves)):
                #         print("Invalid index selected. Try again...")
                #     else:
                #         break  # Break the loop if a valid index has been selected
                # except ValueError:
                #     print("Invalid input! Please enter a number.")
                selected_move_index = 0
                selected_move = legal_moves[selected_move_index]
                print(f"Move chosen: {selected_move}")

                print(f"Move chosen: {convert_move_list_to_pdn([selected_move])}")
                WP, BP, K = do_move(WP, BP, K, selected_move, current_player)
                current_player = switch_player(current_player)

        else:  # AI's turn
            legal_moves = generate_legal_moves(WP, BP, K, current_player)
            if not legal_moves:  # AI has lost
                print("YOU WON!")
                break
            if legal_moves:
                best_move = legal_moves[0]  # Simplified for demonstration
                WP, BP, K = do_move(WP, BP, K, best_move, current_player)
                current_player = switch_player(current_player)
            time.sleep(1)  # Pause for a moment to simulate AI thinking

    pygame.quit()


if __name__ == "__main__":
    main()
