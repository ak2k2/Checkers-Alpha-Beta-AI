import time as t
from typing import List, Tuple, Dict, Set, Union, Optional

import random

from gui.checkerboard_gui import CheckerBoardGUI


def get_blank_board() -> list[list[str]]:
    board = [["." for _ in range(8)] for _ in range(8)]
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


def setup_game() -> tuple[list[list[str]], dict[str, set[tuple[int, int]]]]:
    board = get_blank_board()
    board = setup_board(board)
    player_positions = {
        "X": {
            (row, col) for row in range(8) for col in range(8) if board[row][col] == "X"
        },
        "O": {
            (row, col) for row in range(8) for col in range(8) if board[row][col] == "O"
        },
    }
    return board, player_positions


def player_has_capture(
    player: str, player_positions: dict[str, set[tuple[int, int]]]
) -> bool:
    opponent = "O" if player == "X" else "X"

    # Direction of possible captures based on player
    directions = []
    if player == "X":
        directions = [(2, 2), (2, -2)]
    else:  # 'O'
        directions = [(-2, -2), (-2, 2)]

    # Loop only through player's pieces
    for row, col in player_positions[player]:
        # Check each potential capture move
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            mid_row, mid_col = row + drow // 2, col + dcol // 2

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if (mid_row, mid_col) in player_positions[opponent]:
                    # Check if the destination square is empty
                    if (new_row, new_col) not in player_positions["X"] and (
                        new_row,
                        new_col,
                    ) not in player_positions["O"]:
                        return True

    return False


def piece_has_capture(board: list[list[str]], piece: tuple[int, int]) -> bool:
    row, col = piece
    player = board[row][col]  # either "X" or "O"
    opponent = "O" if player == "X" else "X"  # find the opponent

    # List of potential directions to check for captures
    directions = []
    if player == "X":
        directions = [(1, 1), (1, -1)]
    else:  # 'O'
        directions = [(-1, 1), (-1, -1)]

    for drow, dcol in directions:
        new_row, new_col = row + drow, col + dcol
        jump_row, jump_col = row + 2 * drow, col + 2 * dcol

        # Check if potential capture move is within the board
        if 0 <= jump_row < 8 and 0 <= jump_col < 8:
            # Also check if new_row, new_col is within the board
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                # Check if there is an opponent piece to capture and the landing square is empty
                if (
                    board[new_row][new_col] == opponent
                    and board[jump_row][jump_col] == "."
                ):
                    return True

    return False


def check_if_legal(
    board: list[list[str]],
    player: str,
    move: Union[tuple[tuple[int, int], str], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int], bool]:
    if isinstance(move, str):
        # "0,1->1,0"
        current_row, current_col = map(int, move.split("->")[0].split(","))
        new_row, new_col = map(int, move.split("->")[1].split(","))
    else:
        (current_row, current_col), (new_row, new_col) = move

    if not (
        0 <= current_row <= 7
        and 0 <= current_col <= 7
        and 0 <= new_row <= 7
        and 0 <= new_col <= 7
    ):
        raise Exception("Out of bounds move.")

    current_piece = board[current_row][current_col]
    new_piece = board[new_row][new_col]

    if current_piece != player:
        raise Exception("That is not your piece.")
    if new_piece != ".":
        raise Exception("That space is already occupied.")

    opponent = "O" if player == "X" else "X"

    if (player == "X" and new_row < current_row) or (
        player == "O" and new_row > current_row
    ):
        raise Exception("You cannot move backwards.")

    row_diff = new_row - current_row
    col_diff = new_col - current_col
    if (
        row_diff not in (-2, -1, 1, 2)
        or col_diff not in (-2, -1, 1, 2)
        or abs(row_diff) != abs(col_diff)
    ):
        raise Exception("Invalid move.")

    is_capture = row_diff in (-2, 2)
    if is_capture:
        mid_row, mid_col = (current_row + new_row) // 2, (current_col + new_col) // 2
        if board[mid_row][mid_col] != opponent:
            raise Exception(f"There is no '{opponent}' piece to capture.")

    return (current_row, current_col), (new_row, new_col), is_capture


def update_board(
    current_row: int,
    current_col: int,
    new_row: int,
    new_col: int,
    board: list[list[str]],
    player: str,
    is_capture: bool = False,
) -> list[list[str]]:
    if is_capture:
        mid_row = (new_row + current_row) // 2
        mid_col = (new_col + current_col) // 2
        board[mid_row][mid_col] = "."

    board[current_row][current_col] = "."
    board[new_row][new_col] = player
    return board


def make_move(
    board: list[list[str]],
    move: str,
    player: str,
    checker_board_gui: CheckerBoardGUI,
    player_positions: dict[str, set[tuple[int, int]]],
) -> list[list[str]]:
    while True:
        try:
            (current_row, current_col), (new_row, new_col), is_capture = check_if_legal(
                board, player, move
            )
            break
        except:
            with Exception as e:
                print(e)

            move = input("Please try again: ")

    board = update_board(
        current_row, current_col, new_row, new_col, board, player, is_capture
    )
    if checker_board_gui is not None:
        checker_board_gui.last_moved_piece_coords = (
            new_row,
            new_col,
        )  # <--- For dynamic highlighting
    return board


def generate_capture_moves_from_position(
    board: List[List[str]],
    row: int,
    col: int,
    player: str,
    player_positions: dict[str, set[Tuple[int, int]]],
) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    capture_moves = []
    direction = 1 if player == "X" else -1

    for drow, dcol in [(2 * direction, -2), (2 * direction, 2)]:
        new_row, new_col = row + drow, col + dcol
        move = ((row, col), (new_row, new_col))

        try:
            (_, _, is_capture) = check_if_legal(board, player, move)
            if is_capture:
                capture_moves.append(move)
        except Exception as e:  # It's better to catch specific exceptions
            continue

    return capture_moves


def generate_all_legal_moves(
    board: List[List[str]],
    player: str,
    player_positions: dict[str, set[Tuple[int, int]]],
) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    legal_moves = set()
    capture_moves = set()

    direction = 1 if player == "X" else -1

    if player_has_capture(player, player_positions):
        for row, col in player_positions[player]:
            capture_moves.update(
                generate_capture_moves_from_position(
                    board, row, col, player, player_positions
                )
            )
        return list(capture_moves)

    # If we're here, then there are no capture moves.
    # No need to check for 2-away diagonals.

    for row, col in player_positions[player]:
        for drow, dcol in [(direction, -1), (direction, 1)]:
            new_row, new_col = row + drow, col + dcol
            move = ((row, col), (new_row, new_col))

            try:
                (_, _, is_capture) = check_if_legal(board, player, move)
                # Since we've already determined there are no capture moves,
                # we don't need to check for is_capture again.
                legal_moves.add(move)
            except:  # Catching specific exception types would be better here
                continue

    return list(legal_moves)


def display_board(board: list[list[str]], checker_board_gui: CheckerBoardGUI):
    checker_board_gui.board = board
    checker_board_gui.update_board()
    checker_board_gui.root.update_idletasks()
    checker_board_gui.root.update()


def update_player_positions(
    move: Union[tuple[tuple[int, int], tuple[int, int]], str],
    player: str,
    player_positions: dict[str, set[tuple[int, int]]],
) -> dict[str, set[tuple[int, int]]]:
    if isinstance(move, str):
        # "0,1->1,0"
        current_row, current_col = map(int, move.split("->")[0].split(","))
        new_row, new_col = map(int, move.split("->")[1].split(","))
    else:
        (current_row, current_col), (new_row, new_col) = move

    # Remove the old position
    player_positions[player].remove((current_row, current_col))

    # Add the new position
    player_positions[player].add((new_row, new_col))

    if abs(new_row - current_row) == 2:  # This implies a capture
        opponent = "O" if player == "X" else "X"
        mid_row, mid_col = ((current_row + new_row) // 2, (current_col + new_col) // 2)

        # Remove the captured piece from the opponent's set of positions
        player_positions[opponent].remove((mid_row, mid_col))

    return player_positions


def player_turn(
    board: List[List[str]],
    player: str,
    player_positions: Dict[str, Set[Tuple[int, int]]],
    checker_board_gui: "CheckerBoardGUI",  # Assuming CheckerBoardGUI is the type you'd use
) -> Tuple[Optional[List[List[str]]], Optional[Dict[str, Set[Tuple[int, int]]]], bool]:
    legal_moves = generate_all_legal_moves(board, player, player_positions)

    if not legal_moves:
        return None, None, False  # No legal moves.

    chosen_move = random.choice(legal_moves)

    player_positions = update_player_positions(chosen_move, player, player_positions)
    board = make_move(board, chosen_move, player, checker_board_gui, player_positions)

    # Extract the new row and column
    (_, _), (new_row, new_col) = chosen_move

    # Check if the move was a capture
    if abs(new_row - chosen_move[0][0]) == 2:
        # Check for further jumps
        while True:
            additional_jumps = generate_capture_moves_from_position(
                board, new_row, new_col, player, player_positions
            )
            if not additional_jumps:
                break

            chosen_move = random.choice(additional_jumps)  # No need for tolist()

            player_positions = update_player_positions(
                chosen_move, player, player_positions
            )
            board = make_move(
                board, chosen_move, player, checker_board_gui, player_positions
            )

            # Update new_row and new_col after each additional move
            (_, _), (new_row, new_col) = chosen_move

    return board, player_positions, True


def determine_winner(X_has_moves: bool, O_has_moves: bool) -> str:
    if not O_has_moves and X_has_moves:
        return "X wins!"
    if O_has_moves and not X_has_moves:
        return "O wins!"
    if not O_has_moves and not X_has_moves:
        # TODO: Add the correct board-counting logic here.
        return "It's a tie!"
    return None


def simulate_random_game_gui():
    board, player_positions = setup_game()
    checker_board_gui = CheckerBoardGUI(board)

    t.sleep(3)
    X_has_moves = True
    O_has_moves = True

    delta = 0.05

    while True:
        display_board(board, checker_board_gui)

        board, player_positions, X_has_moves = player_turn(
            board, "X", player_positions, checker_board_gui
        )
        if board is None:
            break
        display_board(board, checker_board_gui)

        t.sleep(delta)

        board, player_positions, O_has_moves = player_turn(
            board, "O", player_positions, checker_board_gui
        )
        if board is None:
            break
        display_board(board, checker_board_gui)

        t.sleep(delta)

        if not X_has_moves and not O_has_moves:
            break

        print("*" * 20)

    winner = determine_winner(X_has_moves, O_has_moves)
    print(winner)


def simulate_random_game_to_time():
    board, player_positions = setup_game()

    X_has_moves = True
    O_has_moves = True

    while True:
        board, player_positions, X_has_moves = player_turn(
            board, "X", player_positions, checker_board_gui=None
        )
        if board is None:
            break

        board, player_positions, O_has_moves = player_turn(
            board, "O", player_positions, checker_board_gui=None
        )
        if board is None:
            break

        if not X_has_moves and not O_has_moves:
            break


if __name__ == "__main__":
    simulate_random_game_gui()
