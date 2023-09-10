import time as t
import numpy as np


from gui.checkerboard_gui import CheckerBoardGUI


def get_blank_board() -> list:
    board = [["." for row in range(8)] for col in range(8)]
    return board


def setup_board(board: list) -> list:
    for row in range(3):
        for col in range(8):
            if (row + col) % 2 != 0:
                board[row][col] = "X"

    for row in range(5, 8):
        for col in range(8):
            if (row + col) % 2 != 0:
                board[row][col] = "O"
    return board


def check_if_legal(board: list, player: str, move: str) -> tuple:
    if len(move.split("->")) != 2:
        raise Exception("Invalid move format.")
    opponent = "O" if player == "X" else "X"

    current_pos, new_pos = move.split("->")
    if len(current_pos.split(",")) != 2 or len(new_pos.split(",")) != 2:
        raise Exception("Invalid position format.")

    current_row, current_col = map(int, current_pos.split(","))
    new_row, new_col = map(int, new_pos.split(","))

    if not (0 <= current_row <= 7) or not (0 <= current_col <= 7):
        raise Exception("Invalid current row or column.")
    if not (0 <= new_row <= 7) or not (0 <= new_col <= 7):
        raise Exception("Invalid new row or column.")

    if board[current_row][current_col] != player:
        raise Exception("That is not your piece.")
    if board[new_row][new_col] == player:
        raise Exception("You cannot move to a space you already occupy.")
    if board[new_row][new_col] == opponent:
        raise Exception(f"You cannot move into {opponent}'s piece.")

    if player == "X" and new_row < current_row:
        raise Exception("You cannot move backwards.")
    if player == "O" and new_row > current_row:
        raise Exception("You cannot move backwards.")

    if not abs(new_row - current_row) == abs(new_col - current_col):
        raise Exception("You can only move diagonally.")

    if not (
        abs(new_row - current_row) in [1, 2] and abs(new_col - current_col) in [1, 2]
    ):
        raise Exception("Invalid move.")

    is_capture = False
    if abs(new_row - current_row) == 2 and abs(new_col - current_col) == 2:
        mid_row, mid_col = (current_row + new_row) // 2, (current_col + new_col) // 2
        if board[mid_row][mid_col] == opponent:
            is_capture = True
        else:
            raise Exception(f"There is no '{opponent}' piece to capture.")

    if player_has_capture(board, player) and not is_capture:
        raise Exception("You have a capture move available. Captures are mandatory.")

    return (current_row, current_col), (new_row, new_col), is_capture


def player_has_capture(board: list, player: str) -> bool:
    opponent = "O" if player == "X" else "X"

    # Direction of possible captures based on player
    directions = []
    if player == "X":
        directions = [(2, 2), (2, -2)]
    else:  # 'O'
        directions = [(-2, -2), (-2, 2)]

    for row in range(8):
        for col in range(8):
            if board[row][col] == player:
                # Check each potential capture move
                for drow, dcol in directions:
                    new_row, new_col = row + drow, col + dcol
                    mid_row, mid_col = row + drow // 2, col + dcol // 2

                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        if (
                            board[new_row][new_col] == "."
                            and board[mid_row][mid_col] == opponent
                        ):
                            return True
    return False


def piece_has_capture(board: list, piece: tuple) -> bool:
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


def make_move(
    current_row, current_col, new_row, new_col, board, player, is_capture: bool = False
) -> list:
    if is_capture:
        mid_row = (new_row + current_row) // 2
        mid_col = (new_col + current_col) // 2
        board[mid_row][mid_col] = "."

    board[current_row][current_col] = "."
    board[new_row][new_col] = player
    return board


def do_move(board: list, move: str, player: str) -> list:
    while True:
        try:
            (current_row, current_col), (new_row, new_col), is_capture = check_if_legal(
                board, player, move
            )
            break
        except:
            move = input("Please try again: ")

    board = make_move(
        current_row, current_col, new_row, new_col, board, player, is_capture
    )

    return board


def generate_all_legal_moves(board: list, player: str, player_positions: list) -> list:
    legal_moves = set()
    capture_moves = set()

    direction = 1 if player == "X" else -1

    for row, col in player_positions[player]:
        for drow, dcol in [(direction, -1), (direction, 1), (2 * direction, -2), (2 * direction, 2)]:
            new_row, new_col = row + drow, col + dcol
            move = f"{row},{col}->{new_row},{new_col}"

            try:
                (_, _, is_capture) = check_if_legal(board, player, move)

                if is_capture:
                    capture_moves.add(move)
                    # Captures are mandatory, so we can break early
                    break
                else:
                    legal_moves.add(move)
            except:  # Catching specific exception types would be better here
                continue

    return list(capture_moves) if capture_moves else list(legal_moves)



def display_board(board, checker_board_gui):
    checker_board_gui.board = board
    checker_board_gui.update_board()
    checker_board_gui.root.update_idletasks()
    checker_board_gui.root.update()


def play_sequence_of_moves(board, moves, checker_board_gui):
    player = "X"  # Starting player is 'X'
    for move in moves:
        input("Press Enter for next move...")
        print(f"\n{player}'s turn with move {move}")
        board = do_move(board, move, player)  # Replace with your move applying logic
        display_board(board, checker_board_gui)

        # Switch player for the next round
        if player == "X":
            player = "O"
        else:
            player = "X"


def update_player_positions(move_str, player, player_positions):
    # Parse the move string to get coordinates
    move_parts = move_str.split("->")
    current_row, current_col = map(int, move_parts[0].split(","))
    new_row, new_col = map(int, move_parts[1].split(","))

    # Remove the old position
    player_positions[player].remove((current_row, current_col))

    # Add the new position
    player_positions[player].add((new_row, new_col))

    # If a capture occurred, remove the captured piece
    mid_row, mid_col = ((current_row + new_row) // 2, (current_col + new_col) // 2)
    if abs(new_row - current_row) == 2:  # This implies a capture
        opponent = "O" if player == "X" else "X"

        # Remove the captured piece from the opponent's set of positions
        player_positions[opponent].remove((mid_row, mid_col))

    return player_positions


def setup_game():
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


def player_turn(board, player, player_positions):
    legal_moves = generate_all_legal_moves(board, player, player_positions)
    if not legal_moves:
        return None, None, False  # Return False to indicate no legal moves.
    chosen_move = np.random.choice(legal_moves).tolist()
    print(f"{player}'s turn with move {chosen_move}")
    board = do_move(board, chosen_move, player)
    player_positions = update_player_positions(chosen_move, player, player_positions)
    return (
        board,
        player_positions,
        True,
    )  # Return True to indicate there were legal moves.


def determine_winner(X_has_moves, O_has_moves):
    if not O_has_moves and X_has_moves:
        return "X wins!"
    if O_has_moves and not X_has_moves:
        return "O wins!"
    if not O_has_moves and not X_has_moves:
        # TODO: Add the correct board-counting logic here.
        return "It's a tie!"
    return None


if __name__ == "__main__":
    GAME_LOG = []
    board, player_positions = setup_game()
    checker_board_gui = CheckerBoardGUI(board)

    t.sleep(2)
    X_has_moves = True
    O_has_moves = True

    while True:
        display_board(board, checker_board_gui)

        board, player_positions, X_has_moves = player_turn(board, "X", player_positions)
        if board is None:
            break
        display_board(board, checker_board_gui)

        t.sleep(1)

        board, player_positions, O_has_moves = player_turn(board, "O", player_positions)
        if board is None:
            break
        display_board(board, checker_board_gui)

        t.sleep(1)

        if not X_has_moves and not O_has_moves:
            break

        print("*" * 20)

    winner = determine_winner(X_has_moves, O_has_moves)
    print(winner)
