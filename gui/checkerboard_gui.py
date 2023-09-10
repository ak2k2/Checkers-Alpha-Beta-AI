import tkinter as tk
from PIL import Image, ImageTk, ImageOps


class CheckerBoardGUI:
    def __init__(self, board):
        self.root = tk.Tk()
        self.root.title("Checkers Board")
        self.root.geometry("1200x1200")  # Manually set the dimensions
        self.board = board
        self.frames = []

        # Load images and make them class attributes
        white_piece_image = Image.open("gui/assets/white.png")
        white_piece_image = white_piece_image.resize((100, 100))
        self.white_piece_image = ImageTk.PhotoImage(white_piece_image)

        black_piece_image = Image.open("gui/assets/black.png")
        black_piece_image = black_piece_image.resize((100, 100))
        self.black_piece_image = ImageTk.PhotoImage(black_piece_image)

        # Create a frame to hold the board, and center it in the window
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(side=tk.TOP, pady=40, padx=50)  # Adjusted padding

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
                frame.grid(row=row + 1, column=col + 1)
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
                frame_bg = frame.cget("bg")  # Get background color of the frame

                if piece == "X":
                    label = tk.Label(frame, image=self.white_piece_image, bg=frame_bg)
                    label.pack()

                elif piece == "O":
                    label = tk.Label(frame, image=self.black_piece_image, bg=frame_bg)
                    label.pack()

    def add_indices(self):
        for i in range(8):
            row_label = tk.Label(
                self.board_frame, text=str(i), fg="white", font="Helvetica 12 bold"
            )
            row_label.grid(row=i + 1, column=0, sticky="w")
            col_label = tk.Label(
                self.board_frame, text=str(i), fg="white", font="Helvetica 12 bold"
            )
            col_label.grid(row=0, column=i + 1, sticky="n")
