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


def generate_all_legal_moves(board: list, player: str) -> list:
    legal_moves = []
    capture_moves = []

    # Direction multiplier: For X, it's +1, for O, it's -1
    direction = 1 if player == "X" else -1

    for row in range(8):
        for col in range(8):
            if board[row][col] == player:
                for drow, dcol in [
                    (direction, -1),
                    (direction, 1),
                    (2 * direction, -2),
                    (2 * direction, 2),
                ]:
                    new_row, new_col = row + drow, col + dcol
                    move = f"{row},{col}->{new_row},{new_col}"

                    try:
                        (
                            (current_row, current_col),
                            (new_row, new_col),
                            is_capture,
                        ) = check_if_legal(board, player, move)

                        if is_capture:
                            capture_moves.append(move)
                        else:
                            legal_moves.append(move)
                    except:  # Catching specific exception types would be better here
                        continue

    return capture_moves if capture_moves else legal_moves


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


if __name__ == "__main__":
    GAME_LOG = []
    board = get_blank_board()
    board = setup_board(board)
    checker_board_gui = CheckerBoardGUI(board)
    t.sleep(2)
    while True:
        display_board(board, checker_board_gui)
        X_legal_moves = generate_all_legal_moves(board, "X")
        if len(X_legal_moves) == 0:
            break
        X_rand_choice = np.random.choice(X_legal_moves)
        print(f"X's turn with move {X_rand_choice}")
        GAME_LOG.append(X_rand_choice)
        t.sleep(0.5)
        board = do_move(board, X_rand_choice, "X")
        display_board(board, checker_board_gui)

        O_legal_moves = generate_all_legal_moves(board, "O")
        if len(O_legal_moves) == 0:
            break
        O_rand_choice = np.random.choice(O_legal_moves)
        print(f"O's turn with move {O_rand_choice}")
        GAME_LOG.append(O_rand_choice)
        t.sleep(0.5)
        board = do_move(board, O_rand_choice, "O")

        print("*" * 20)

    print(GAME_LOG)

    if len(O_legal_moves) == 0 and len(X_legal_moves) != 0:
        print("X wins!")
    if len(O_legal_moves) != 0 and len(X_legal_moves) == 0:
        print("O wins!")
    if len(O_legal_moves) == 0 and len(X_legal_moves) == 0:
        if board.count("X") > board.count("O"):
            print("X wins!")
        elif board.count("X") < board.count("O"):
            print("O wins!")
        else:
            print("It's a tie!")

    # moves = [
    #     "2,5->3,4",
    #     "5,4->4,3",
    #     "2,1->3,0",
    #     "4,3->2,5",
    #     "1,4->3,6",
    #     "5,0->4,1",
    #     "1,2->2,1",
    #     "4,1->3,2",
    #     "2,1->4,3",
    #     "5,2->3,4",
    #     "2,3->4,5",
    #     "5,6->3,4",
    #     "3,6->4,7",
    #     "6,7->5,6",
    #     "1,0->2,1",
    #     "6,3->5,2",
    #     "0,1->1,2",
    #     "5,6->4,5",
    #     "4,7->5,6",
    #     "6,5->4,7",
    #     "1,6->2,5",
    #     "3,4->1,6",
    #     "0,7->2,5",
    #     "5,2->4,1",
    #     "3,0->5,2",
    #     "6,1->4,3",
    #     "2,1->3,2",
    #     "4,3->2,1",
    #     "1,2->3,0",
    #     "7,2->6,3",
    #     "0,3->1,2",
    #     "6,3->5,4",
    #     "1,2->2,1",
    #     "7,4->6,3",
    #     "2,1->3,2",
    #     "4,5->3,4",
    #     "2,5->4,3",
    #     "7,6->6,5",
    #     "2,7->3,6",
    #     "4,7->2,5",
    #     "3,2->4,1",
    #     "5,4->3,2",
    # ]
    # play_sequence_of_moves(board, moves, checker_board_gui)
