import tkinter as tk
from PIL import Image, ImageTk, ImageDraw


def add_overlay(image, overlay_color=(255, 255, 0, 100)):
    overlay = Image.new("RGBA", image.size, overlay_color)
    output = Image.alpha_composite(image.convert("RGBA"), overlay)
    return output


class CheckerBoardGUI:
    def __init__(self, board):
        self.root = tk.Tk()
        self.root.title("Checkers Board")
        self.root.geometry("1200x1200")  # Manually set the dimensions
        self.board = board
        self.frames = []
        self.last_moved_piece_coords = None

        # Load images
        white_piece_image = Image.open("gui/assets/white.png").resize((100, 100))
        self.white_piece_image = ImageTk.PhotoImage(white_piece_image)

        black_piece_image = Image.open("gui/assets/black.png").resize((100, 100))
        self.black_piece_image = ImageTk.PhotoImage(black_piece_image)

        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(side=tk.TOP, pady=40, padx=50)
        self.add_indices()
        self.init_board()

    def init_board(self):
        for row in range(8):
            row_frames = []
            for col in range(8):
                color = "black" if (row + col) % 2 == 0 else "red"
                frame = tk.Frame(self.board_frame, width=100, height=100, bg=color)
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
                if (row, col) == self.last_moved_piece_coords:
                    frame.config(bg="yellow")
                else:
                    frame.config(bg="black" if (row + col) % 2 == 0 else "red")

                if piece == "X":
                    label = tk.Label(
                        frame, image=self.white_piece_image, bg=frame.cget("bg")
                    )
                    label.pack()
                elif piece == "O":
                    label = tk.Label(
                        frame, image=self.black_piece_image, bg=frame.cget("bg")
                    )
                    label.pack()

    def add_indices(self):
        for i in range(8):
            row_label = tk.Label(
                self.board_frame, text=str(i), fg="white", font="Helvetica 15 bold"
            )
            row_label.grid(row=i + 1, column=0, sticky="w")
            col_label = tk.Label(
                self.board_frame, text=str(i), fg="white", font="Helvetica 15 bold"
            )
            col_label.grid(row=0, column=i + 1, sticky="n")
