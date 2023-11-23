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
KINGS_MARK = hex_to_rgb("#2596BE")

HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow
TRANSPARENCY = 40  # Alpha value, 0 is fully transparent, 255 is opaque

CIRCLE_RADIUS = (SQUARE_SIZE // 2 - 10) * 0.3  # 20% of the piece's radius
CIRCLE_COLOR = (80, 80, 80, 60)  # Grey with transparency


def draw_board(win):
    win.fill(UNPLAYABLE_COLOR)
    for row in range(ROWS):
        for col in range(row % 2, ROWS, 2):
            pygame.draw.rect(
                win,
                PLAYABLE_COLOR,
                (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            )


def draw_indices(win):
    font = pygame.font.SysFont("Arial", 24)
    letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
    numbers = ["1", "2", "3", "4", "5", "6", "7", "8"]

    # Draw column letters
    for i, letter in enumerate(letters):
        text = font.render(letter, True, (0, 0, 0))
        win.blit(
            text,
            (i * SQUARE_SIZE + SQUARE_SIZE // 2 - text.get_width() // 2, HEIGHT - 30),
        )
        win.blit(text, (i * SQUARE_SIZE + SQUARE_SIZE // 2 - text.get_width() // 2, 10))

    # Draw row numbers
    for i, number in enumerate(numbers):
        text = font.render(number, True, (0, 0, 0))
        win.blit(
            text,
            (WIDTH - 30, i * SQUARE_SIZE + SQUARE_SIZE // 2 - text.get_height() // 2),
        )
        win.blit(
            text, (10, i * SQUARE_SIZE + SQUARE_SIZE // 2 - text.get_height() // 2)
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


def draw_king(win, row, col, color, offset=None):
    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

    if offset:
        center_x += offset[0]
        center_y += offset[1]

    pygame.draw.circle(win, color, (center_x, center_y), SQUARE_SIZE // 2 - 10)
    pygame.draw.circle(win, KINGS_MARK, (center_x, center_y), SQUARE_SIZE // 8)


def draw_pieces(win, WP, BP, K, dragging, drag_pos, selected_piece):
    for row in range(ROWS):
        for col in range(COLS):
            index = (7 - row) * 4 + (col // 2)  # Moved index calculation here

            if row % 2 != col % 2:
                is_king = K & MASK_32 & (1 << index)
                if WP & MASK_32 & (1 << index):
                    if is_king:
                        draw_king(win, row, col, WHITE)
                    else:
                        draw_piece(win, row, col, WHITE)
                elif BP & MASK_32 & (1 << index):
                    if is_king:
                        draw_king(win, row, col, BLACK)
                    else:
                        draw_piece(win, row, col, BLACK)

            if dragging and index == selected_piece:
                piece_color = WHITE if WP & MASK_32 & (1 << selected_piece) else BLACK
                piece_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                piece_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                offset_x = drag_pos[0] - piece_x
                offset_y = drag_pos[1] - piece_y
                draw_king(
                    win, row, col, piece_color, (offset_x, offset_y)
                ) if K & MASK_32 & (1 << selected_piece) else draw_piece(
                    win, row, col, piece_color, (offset_x, offset_y)
                )


def coordinates_to_bit(row, col):
    adjusted_row = 7 - row
    bit_index = adjusted_row * 4 + col // 2
    return bit_index


def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Checkers AI")
    # Create a Surface with per-pixel alpha
    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE)).convert_alpha()
    highlight_surface.fill(
        (*HIGHLIGHT_COLOR, TRANSPARENCY)
    )  # Fill with transparent color

    # Create a Surface for the legal move circles
    circle_surface = pygame.Surface(
        (CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2), pygame.SRCALPHA
    )
    pygame.draw.circle(
        circle_surface, CIRCLE_COLOR, (CIRCLE_RADIUS, CIRCLE_RADIUS), CIRCLE_RADIUS
    )

    WP, BP, K = get_fresh_board()
    # WP, BP, K = setup_board_from_position_lists(
    #     white_positions=["KC1", "KE1"], black_positions=["F6", "F4", "D2", "F2"]
    # )
    temp_WP, temp_BP, temp_K = WP, BP, K  # Temporary board states

    human_color = PlayerTurn.BLACK
    current_player = PlayerTurn.BLACK
    selected_piece = None
    legal_moves = None

    dragging = False
    drag_pos = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if (
                event.type == pygame.MOUSEBUTTONDOWN and current_player == human_color
            ):  # Human's turn
                pos = pygame.mouse.get_pos()
                row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE

                if row % 2 != col % 2:  # Clicked on a playable square
                    bit_index = coordinates_to_bit(row, col)

                    is_human_piece = (
                        (WP & MASK_32 & (1 << bit_index))
                        if human_color == PlayerTurn.WHITE
                        else (BP & MASK_32 & (1 << bit_index))
                    )

                    if is_human_piece:  # Clicked on a human piece
                        print(f"Clicked on piece at {row}, {col}")

                        # temp_WP = (
                        #     remove_piece(WP, bit_index)
                        #     if human_color == PlayerTurn.WHITE
                        #     else WP
                        # )
                        # temp_BP = (
                        #     remove_piece(BP, bit_index)
                        #     if human_color == PlayerTurn.BLACK
                        #     else BP
                        # )
                        if (
                            selected_piece is None or selected_piece != bit_index
                        ):  # Selecting a fresh piece
                            print(f"Selected a fresh piece at {row}, {col}")
                            selected_piece = bit_index
                            legal_moves = generate_legal_moves(
                                WP, BP, K, current_player
                            )
                            print(f"Legal moves: {legal_moves}")
                            dragging = True
                            drag_pos = pos
                        else:
                            print(f"Deselected piece")
                            selected_piece = None
                            dragging = False

            elif (
                event.type == pygame.MOUSEBUTTONUP and dragging
            ):  # Human is dragging a piece
                end_pos = pygame.mouse.get_pos()
                end_row, end_col = end_pos[1] // SQUARE_SIZE, end_pos[0] // SQUARE_SIZE

                if end_row % 2 != end_col % 2:  # Clicked on a playable square
                    destination = coordinates_to_bit(end_row, end_col)
                    valid_move = False
                    move_to_make = None

                    for move in legal_moves:
                        if isinstance(move, list):  # Handle multi-jump
                            if move[0] == selected_piece and move[-1] == destination:
                                valid_move = True
                                move_to_make = move
                                break
                        elif move == [
                            selected_piece,
                            destination,
                        ] or move == (
                            selected_piece,
                            destination,
                        ):  # Handle single move/jump
                            valid_move = True
                            move_to_make = move
                            break

                    if valid_move:
                        WP, BP, K = do_move(WP, BP, K, move_to_make, current_player)
                        current_player = switch_player(current_player)
                        selected_piece = None
                        temp_WP, temp_BP, temp_K = (
                            WP,
                            BP,
                            K,
                        )  # reset temporary board states
                    else:
                        print("Invalid move!")
                        temp_WP, temp_BP, temp_K = (
                            WP,
                            BP,
                            K,
                        )
                else:  # Clicked on an unplayable square
                    print("Invalid move!")
                    temp_WP, temp_BP, temp_K = (
                        WP,
                        BP,
                        K,
                    )
                dragging = False
                drag_pos = None

            elif event.type == pygame.MOUSEMOTION and dragging:
                drag_pos = pygame.mouse.get_pos()
                temp_WP = (
                    remove_piece(WP, bit_index)
                    if human_color == PlayerTurn.WHITE
                    else WP
                )
                temp_BP = (
                    remove_piece(BP, bit_index)
                    if human_color == PlayerTurn.BLACK
                    else BP
                )

        draw_board(win)
        draw_pieces(win, temp_WP, temp_BP, temp_K, dragging, drag_pos, selected_piece)
        draw_indices(win)

        if selected_piece is not None:  # HIGHLIGHTING LOGIC
            adjusted_row = 7 - (selected_piece // 4)
            col = (selected_piece % 4) * 2
            if adjusted_row % 2 == 0:
                col += 1
            win.blit(
                highlight_surface,
                (col * SQUARE_SIZE, adjusted_row * SQUARE_SIZE),
            )

            for move in legal_moves:  # Highlight legal move paths
                if isinstance(move, tuple) and move[0] == selected_piece:
                    adjusted_row = 7 - (move[1] // 4)
                    col = (move[1] % 4) * 2
                    if adjusted_row % 2 == 0:
                        col += 1

                    circle_x = col * SQUARE_SIZE + SQUARE_SIZE // 2 - CIRCLE_RADIUS
                    circle_y = (
                        adjusted_row * SQUARE_SIZE + SQUARE_SIZE // 2 - CIRCLE_RADIUS
                    )

                    win.blit(circle_surface, (circle_x, circle_y))

                elif isinstance(move, list) and move[0] == selected_piece:
                    for step in move[1:]:
                        adjusted_row = 7 - (step // 4)
                        col = (step % 4) * 2
                        if adjusted_row % 2 == 0:
                            col += 1

                        circle_x = col * SQUARE_SIZE + SQUARE_SIZE // 2 - CIRCLE_RADIUS
                        circle_y = (
                            adjusted_row * SQUARE_SIZE
                            + SQUARE_SIZE // 2
                            - CIRCLE_RADIUS
                        )

                        win.blit(circle_surface, (circle_x, circle_y))

        pygame.display.update()
        clock.tick(60)

        if current_player != human_color:  # AI's turn
            legal_moves = generate_legal_moves(WP, BP, K, current_player)
            if not legal_moves:
                print("YOU WON!")
                break
            if legal_moves:
                best_move, _ = AI(
                    position=(WP, BP, K),
                    current_player=current_player,
                    time_limit=3,
                    heuristic="smart",
                    global_board_state=(WP, BP, K),
                )
                WP, BP, K = do_move(WP, BP, K, best_move, current_player)
                current_player = switch_player(current_player)

            temp_WP, temp_BP, temp_K = WP, BP, K  # reset temporary board states
            time.sleep(1)

    pygame.quit()


if __name__ == "__main__":
    main()
