import ast
import random
import time as t
from typing import Dict, List, Optional, Set, Tuple, Union

from gui.checkerboard_gui import CheckerBoardGUI


def display_board(board: list[list[str]], checker_board_gui: CheckerBoardGUI):
    checker_board_gui.board = board
    checker_board_gui.update_board()
    checker_board_gui.root.update_idletasks()
    checker_board_gui.root.update()


def get_blank_board() -> list[list[str]]:
    board = [["." for _ in range(8)] for _ in range(8)]
    return board


def construct_board_from_player_positions(
    player_positions: dict[str, set[tuple[int, int]]]
) -> list[list[str]]:
    board = get_blank_board()
    for row, col in player_positions["X"]:
        board[row][col] = "X"
    for row, col in player_positions["O"]:
        board[row][col] = "O"
    for row, col in player_positions["XK"]:
        board[row][col] = "XK"
    for row, col in player_positions["OK"]:
        board[row][col] = "OK"
    return board


def setup_board(board: list[list[str]]) -> list[list[str]]:
    for row in range(3):
        for col in range(8):
            if (row + col) % 2 != 0:
                board[row][col] = "X"

    for row in range(5, 8):
        for col in range(8):
            if (row + col) % 2 != 0:
                board[row][col] = "O"
    return board


def get_player_positions(board: list[list[str]]) -> dict[str, set[tuple[int, int]]]:
    return {
        "X": {
            (row, col) for row in range(8) for col in range(8) if board[row][col] == "X"
        },
        "O": {
            (row, col) for row in range(8) for col in range(8) if board[row][col] == "O"
        },
        "XK": {
            (row, col)
            for row in range(8)
            for col in range(8)
            if board[row][col] == "XK"
        },
        "OK": {
            (row, col)
            for row in range(8)
            for col in range(8)
            if board[row][col] == "OK"
        },
    }


def setup_game() -> tuple[list[list[str]], dict[str, set[tuple[int, int]]]]:
    board = get_blank_board()
    board = setup_board(board)
    player_positions = {
        "X": set(),
        "O": set(),
        "XK": set(),
        "OK": set(),
    }
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != ".":
                player_positions[piece].add((row, col))
    return board, player_positions


def get_directions(player: str) -> List[Tuple[int, int]]:
    if player == "X":
        return [(1, 1), (1, -1)]
    elif player == "XK":
        return [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    elif player == "O":
        return [(-1, 1), (-1, -1)]
    elif player == "OK":
        return [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def player_has_capture(
    player: str, player_positions: dict[str, set[tuple[int, int]]]
) -> bool:
    # Determine the opponent pieces based on the player
    if player in ["X", "XK"]:
        opponent_pieces = ["O", "OK"]
    else:
        opponent_pieces = ["X", "XK"]

    # Direction of possible captures based on player
    directions = []
    if player == "X":
        directions = [(2, 2), (2, -2)]
    elif player == "O":
        directions = [(-2, -2), (-2, 2)]
    elif player == "XK":
        directions = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
    elif player == "OK":
        directions = [(2, 2), (2, -2), (-2, 2), (-2, -2)]

    # Loop only through player's pieces
    for row, col in player_positions[player]:
        # Check each potential capture move
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            mid_row, mid_col = row + drow // 2, col + dcol // 2

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                # Check if there's an opponent piece to capture
                if any(
                    [
                        (mid_row, mid_col) in player_positions[op]
                        for op in opponent_pieces
                    ]
                ):
                    # Check if the destination square is empty
                    if (
                        (new_row, new_col) not in player_positions["X"]
                        and (new_row, new_col) not in player_positions["XK"]
                        and (new_row, new_col) not in player_positions["O"]
                        and (new_row, new_col) not in player_positions["OK"]
                    ):
                        return True

    return False


def generate_capture_moves_from_position(
    board: List[List[str]],
    row: int,
    col: int,
    player: str,
) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    capture_moves = []
    if player == "X":
        directions = [(2, 2), (2, -2)]
    elif player == "O":
        directions = [(-2, 2), (-2, -2)]
    elif player == "XK":
        directions = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
    elif player == "OK":
        directions = [(2, 2), (2, -2), (-2, 2), (-2, -2)]

    for d in directions:
        new_row, new_col = row + d[0], col + d[1]
        mid_row, mid_col = row + d[0] // 2, col + d[1] // 2

        if 0 <= new_row < 8 and 0 <= new_col < 8:
            if board[mid_row][mid_col] == ".":  # There is no opponent piece to capture
                continue

            elif board[new_row][new_col] != ".":  # The destination square is not empty
                continue

            else:
                if player == "X" or player == "XK":
                    if (
                        board[mid_row][mid_col] == "O"
                        or board[mid_row][mid_col] == "OK"
                    ):
                        capture_moves.append(((row, col), (new_row, new_col)))
                elif player == "O" or player == "OK":
                    if (
                        board[mid_row][mid_col] == "X"
                        or board[mid_row][mid_col] == "XK"
                    ):
                        capture_moves.append(((row, col), (new_row, new_col)))
    return capture_moves


def generate_all_legal_moves(
    board: List[List[str]],
    player: str,
    player_positions: dict[str, set[Tuple[int, int]]],
) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    def is_legal(
        board: list[list[str]],
        player: str,
        move: tuple,
    ) -> bool:
        (current_row, current_col), (new_row, new_col) = move

        if not (
            0 <= current_row <= 7
            and 0 <= current_col <= 7
            and 0 <= new_row <= 7
            and 0 <= new_col <= 7
        ):
            return False

        current_piece = board[current_row][current_col]
        new_piece = board[new_row][new_col]

        if current_piece != player:
            return False
        if new_piece != ".":
            return False

        opponent = "O" if player == "X" or player == "XK" else "X"

        if (player == "X" and new_row < current_row) or (
            player == "O" and new_row > current_row
        ):
            return False

        row_diff = new_row - current_row

        is_capture = row_diff in (-2, 2)
        if is_capture:
            mid_row, mid_col = (current_row + new_row) // 2, (
                current_col + new_col
            ) // 2
            if board[mid_row][mid_col] != opponent:
                return False

        return True

    if player_has_capture(
        player, player_positions
    ):  # a capture must be done if possible
        print(f"player {player} has a capture")
        capture_moves = set()
        for row, col in player_positions[player]:
            capture_moves.update(
                generate_capture_moves_from_position(board, row, col, player)
            )
        return list(capture_moves)

    else:  # no captures availible
        legal_moves = set()
        directions = get_directions(player)

        for direction in directions:
            for row, col in player_positions[player]:
                new_row, new_col = row + direction[0], col + direction[1]
                move = ((row, col), (new_row, new_col))

                if is_legal(board, player, move):
                    legal_moves.add(move)

        return list(legal_moves)


def piece_has_capture(board: list[list[str]], piece: tuple[int, int]) -> bool:
    row, col = piece
    player = board[row][col]  # either "X", "XK", "O", or "OK"

    # Determine the opponent pieces based on the player
    if player in ["X", "XK"]:
        opponent_pieces = ["O", "OK"]
    else:
        opponent_pieces = ["X", "XK"]

    # List of potential directions to check for captures
    directions = []
    if player in ["X", "XK"]:
        directions = [(1, 1), (1, -1)]
    if player in ["O", "OK"]:
        directions.extend([(-1, 1), (-1, -1)])

    for drow, dcol in directions:
        new_row, new_col = row + drow, col + dcol
        jump_row, jump_col = row + 2 * drow, col + 2 * dcol

        # Check if potential capture move is within the board
        if 0 <= jump_row < 8 and 0 <= jump_col < 8:
            # Also check if new_row, new_col is within the board
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                # Check if there is an opponent piece to capture and the landing square is empty
                if (
                    board[new_row][new_col] in opponent_pieces
                    and board[jump_row][jump_col] == "."
                ):
                    return True

    return False


def make_move(board: list[list[str]], player: str, M) -> list[list[str]]:
    player_positions = get_player_positions(board)
    turn = True
    while turn:
        legal_moves = generate_all_legal_moves(board, player, player_positions)
        print(f"Legal moves for {player}: {legal_moves}")
        # move_str = input(f"{player} to move: ")
        # move = ast.literal_eval(move_str)
        move = getMove(M)

        if move not in legal_moves:
            raise Exception("Illegal move.")
        else:
            (current_row, current_col), (new_row, new_col) = move

        # Check for promotion to king
        if player == "X" and new_row == 7:
            board[new_row][new_col] = "XK"
            player_positions["X"].remove((new_row, new_col))
            player_positions["XK"].add((new_row, new_col))
        elif player == "O" and new_row == 0:
            board[new_row][new_col] = "OK"
            player_positions["O"].remove((new_row, new_col))
            player_positions["OK"].add((new_row, new_col))

        # Remove the old position
        player_positions[player].remove((current_row, current_col))
        # Add the new position
        player_positions[player].add((new_row, new_col))

        # Update the board
        board = construct_board_from_player_positions(player_positions)

        if abs(new_row - current_row) == 2:  # Capture
            mid_row, mid_col = (
                (current_row + new_row) // 2,
                (current_col + new_col) // 2,
            )
            opponent = "O" if player == "X" else "X"
            # Remove the captured piece from the opponent's set of positions
            player_positions[opponent].remove((mid_row, mid_col))

            # Update the board to remove the captured piece
            board[mid_row][mid_col] = "."

            # Check if the piece that just captured has another capture opportunity
            if piece_has_capture(board, (new_row, new_col)):
                # Create a modified player_positions dictionary with only the relevant piece
                modified_player_positions = {
                    player: {(new_row, new_col)},
                    opponent: player_positions[opponent],
                }
                # Generate legal moves for the piece that just captured
                legal_moves = generate_all_legal_moves(
                    board, player, modified_player_positions
                )
                if legal_moves:
                    turn = True
                    continue  # Continue to the next iteration of the while loop
                else:
                    turn = False
            else:
                turn = False
        else:
            turn = False
    return board


def getMove(num):
    moves_made = [
        ((5, 4), (4, 5)),
        ((2, 3), (3, 2)),
        ((6, 3), (5, 4)),
        ((3, 2), (4, 1)),
        ((5, 0), (3, 2)),
        ((2, 1), (4, 3)),
        ((5, 2), (3, 4)),
        ((2, 5), (4, 3)),
        ((5, 4), (3, 2)),
        ((1, 2), (2, 3)),
        ((6, 1), (5, 2)),
        ((2, 3), (4, 1)),
    ]
    return moves_made[num]


if __name__ == "__main__":
    board, player_positions = setup_game()
    checker_board_gui = CheckerBoardGUI(board)
    player_positions = get_player_positions(board)
    M = 0
    while True:
        display_board(board, checker_board_gui)
        board = make_move(board, "O", M)
        M += 1
        t.sleep(1)
        display_board(board, checker_board_gui)
        board = make_move(board, "X", M)
        M += 1
        t.sleep(1)
        display_board(board, checker_board_gui)
