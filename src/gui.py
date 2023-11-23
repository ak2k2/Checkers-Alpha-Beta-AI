import time
import pygame
from checkers import *
from heuristic import *
from minimax_alphabeta import AI
from util.helpers import *

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


PLAYABLE_COLOR = hex_to_rgb("#D0AE8B")
UNPLAYABLE_COLOR = hex_to_rgb("#976C40")
WHITE = hex_to_rgb("#DEC5AB")
BLACK = hex_to_rgb("#180000")
HIGHLIGHT = (255, 255, 0)


def draw_board(win):
    win.fill(UNPLAYABLE_COLOR)
    for row in range(ROWS):
        for col in range(row % 2, ROWS, 2):
            pygame.draw.rect(
                win,
                PLAYABLE_COLOR,
                (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            )


def draw_piece(win, row, col, color, offset=None):
    if offset:
        pygame.draw.circle(
            win,
            color,
            (
                col * SQUARE_SIZE + SQUARE_SIZE // 2 + offset[0],
                row * SQUARE_SIZE + SQUARE_SIZE // 2 + offset[1],
            ),
            SQUARE_SIZE // 2 - 10,
        )
    else:
        pygame.draw.circle(
            win,
            color,
            (
                col * SQUARE_SIZE + SQUARE_SIZE // 2,
                row * SQUARE_SIZE + SQUARE_SIZE // 2,
            ),
            SQUARE_SIZE // 2 - 10,
        )


def draw_king(win, row, col, color):
    points = [
        (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + 10),
        (col * SQUARE_SIZE + 10, row * SQUARE_SIZE + SQUARE_SIZE - 10),
        (col * SQUARE_SIZE + SQUARE_SIZE - 10, row * SQUARE_SIZE + SQUARE_SIZE - 10),
    ]
    pygame.draw.polygon(win, color, points)


def draw_pieces(win, WP, BP, K, dragging, drag_pos, selected_piece):
    for row in range(ROWS):
        for col in range(COLS):
            index = (7 - row) * 4 + (col // 2)  # Moved index calculation here

            if row % 2 != col % 2:
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

            if dragging and index == selected_piece:
                piece_color = WHITE if WP & (1 << selected_piece) else BLACK
                if K & (1 << selected_piece):
                    draw_king(win, row, col, piece_color)
                else:
                    piece_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                    piece_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                    offset_x = drag_pos[0] - piece_x
                    offset_y = drag_pos[1] - piece_y
                    draw_piece(win, row, col, piece_color, (offset_x, offset_y))


def coordinates_to_bit(row, col):
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

    WP, BP, K = get_fresh_board()
    human_color = PlayerTurn.WHITE
    current_player = PlayerTurn.BLACK
    selected_piece = None
    legal_moves = None

    dragging = False
    drag_start_pos = None
    drag_pos = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and current_player == human_color:
                pos = pygame.mouse.get_pos()
                row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE

                if row % 2 != col % 2:
                    bit_index = coordinates_to_bit(row, col)

                    is_human_piece = (
                        (WP & (1 << bit_index))
                        if human_color == PlayerTurn.WHITE
                        else (BP & (1 << bit_index))
                    )

                    if is_human_piece:
                        if selected_piece is None or selected_piece != bit_index:
                            selected_piece = bit_index
                            legal_moves = generate_legal_moves(
                                WP, BP, K, current_player
                            )
                            dragging = True
                            drag_start_pos = pos
                            drag_pos = pos
                        else:
                            selected_piece = None
                            dragging = False

            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                end_pos = pygame.mouse.get_pos()
                end_row, end_col = end_pos[1] // SQUARE_SIZE, end_pos[0] // SQUARE_SIZE

                if end_row % 2 != end_col % 2:
                    destination = coordinates_to_bit(end_row, end_col)
                    if [selected_piece, destination] in legal_moves or (
                        selected_piece,
                        destination,
                    ) in legal_moves:
                        WP, BP, K = do_move(
                            WP, BP, K, (selected_piece, destination), current_player
                        )
                        current_player = switch_player(current_player)
                        selected_piece = None

                dragging = False
                drag_start_pos = None
                drag_pos = None

            elif event.type == pygame.MOUSEMOTION and dragging:
                drag_pos = pygame.mouse.get_pos()

        draw_board(win)
        draw_pieces(win, WP, BP, K, dragging, drag_pos, selected_piece)
        remove_piece

        if selected_piece is not None and not dragging:
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

        if current_player != human_color:
            legal_moves = generate_legal_moves(WP, BP, K, current_player)
            if not legal_moves:
                print("YOU WON!")
                break
            if legal_moves:
                best_move = random.choice(legal_moves)
                WP, BP, K = do_move(WP, BP, K, best_move, current_player)
                current_player = switch_player(current_player)
            time.sleep(1)

    pygame.quit()


if __name__ == "__main__":
    main()
