import tkinter as tk


class CheckerBoardGUI:
    def __init__(self, board):
        self.root = tk.Tk()
        self.root.title("Checkers Board")
        self.board = board
        self.frames = []

        # Create a frame to hold the board, and center it in the window
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(side=tk.TOP, pady=50, padx=50)

        self.add_indices()
        self.init_board()

    def init_board(self):
        for row in range(8):
            row_frames = []
            for col in range(8):
                if (row + col) % 2 == 0:
                    background_color = "black"
                else:
                    background_color = "red"

                frame = tk.Frame(
                    self.board_frame, width=100, height=100, bg=background_color
                )
                frame.grid(
                    row=row + 1, column=col + 1
                )  # Shifted down by 1 row and 1 column
                frame.pack_propagate(False)
                row_frames.append(frame)
            self.frames.append(row_frames)
        self.update_board()

    def update_board(self):
        for row in range(8):
            for col in range(8):
                frame = self.frames[row][col]
                for widget in frame.winfo_children():
                    widget.destroy()

                piece = self.board[row][col]
                if piece == "X":
                    circle_color = "white"
                elif piece == "O":
                    circle_color = "black"
                else:
                    circle_color = None

                if circle_color:
                    canvas = tk.Canvas(
                        frame,
                        width=100,
                        height=100,
                        bg=frame["bg"],
                        highlightthickness=0,
                    )
                    canvas.pack(fill=tk.BOTH, expand=1)
                    canvas.create_oval(20, 20, 80, 80, fill=circle_color)

    def add_indices(self):
        for i in range(8):
            row_label = tk.Label(
                self.board_frame, text=str(i), fg="white", font="Helvetica 12 bold"
            )
            row_label.grid(row=i + 1, column=0, sticky="w")  # Shifted down by 1 row
            col_label = tk.Label(
                self.board_frame, text=str(i), fg="white", font="Helvetica 12 bold"
            )
            col_label.grid(
                row=0, column=i + 1, sticky="n"
            )  # Shifted to the right by 1 column
