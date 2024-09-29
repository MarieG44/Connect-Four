
import tkinter as tk
from tkinter import messagebox
import math
import random

# Constants
ROWS = 6
COLUMNS = 7
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4
MAX_DEPTH = 5  # Maximum depth for minimax

# Create the game board
def create_board():
    return [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]

# Function to check if a column is valid for a move
def is_valid_column(board, col):
    return board[0][col] == EMPTY

# Function to get the next open row in a column
def get_next_open_row(board, col):
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == EMPTY:
            return r

# Function to drop a piece into the board
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# Function to check for a win
def check_win(board, piece):
    # Horizontal check
    for c in range(COLUMNS-3):
        for r in range(ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    # Vertical check
    for c in range(COLUMNS):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    # Positive diagonal check
    for c in range(COLUMNS-3):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    # Negative diagonal check
    for c in range(COLUMNS-3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

# Function to check if the board is full
def is_board_full(board):
    return all(board[0][col] != EMPTY for col in range(COLUMNS))

# Function to evaluate a window for the minimax algorithm
def evaluate_window(window, piece):
    score = 0
    opponent_piece = PLAYER_PIECE if piece == AI_PIECE else PLAYER_PIECE
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opponent_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score

# Function to evaluate the whole board for the minimax algorithm
def score_position(board, piece):
    score = 0
    # Score center column
    center_array = [board[r][COLUMNS//2] for r in range(ROWS)]
    center_count = center_array.count(piece)
    score += center_count * 3
    # Score horizontal
    for r in range(ROWS):
        row_array = [board[r][c] for c in range(COLUMNS)]
        for c in range(COLUMNS-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    # Score vertical
    for c in range(COLUMNS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    # Score positive diagonal
    for r in range(ROWS-3):
        for c in range(COLUMNS-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    # Score negative diagonal
    for r in range(ROWS-3):
        for c in range(COLUMNS-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    return score

# Get all valid columns
def get_valid_columns(board):
    return [col for col in range(COLUMNS) if is_valid_column(board, col)]

# Function to check if it's a terminal node
def is_terminal_node(board):
    return check_win(board, PLAYER_PIECE) or check_win(board, AI_PIECE) or is_board_full(board)

# Minimax function with Alpha-Beta Pruning
def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_columns = get_valid_columns(board)
    terminal = is_terminal_node(board)
    if depth == 0 or terminal:
        if terminal:
            if check_win(board, AI_PIECE):
                return (None, 100000000000000)
            elif check_win(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:  # Game over
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        best_column = random.choice(valid_columns)
        for col in valid_columns:
            row = get_next_open_row(board, col)
            board_copy = [r[:] for r in board]  # Deep copy of the board
            drop_piece(board_copy, row, col, AI_PIECE)
            new_score = minimax(board_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_column, value
    else:  # Minimizing player
        value = math.inf
        best_column = random.choice(valid_columns)
        for col in valid_columns:
            row = get_next_open_row(board, col)
            board_copy = [r[:] for r in board]  # Deep copy of the board
            drop_piece(board_copy, row, col, PLAYER_PIECE)
            new_score = minimax(board_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_column, value

# GUI class for Connect Four
class ConnectFourGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect Four")
        self.board = create_board()
        self.buttons = []
        self.canvas = tk.Canvas(root, width=700, height=600, bg="blue")
        self.canvas.pack()
        self.create_board_gui()

    def create_board_gui(self):
        # Create column buttons
        for col in range(COLUMNS):
            button = tk.Button(self.root, text=f"Drop in {col+1}", width=13, command=lambda col=col: self.player_move(col))
            button.pack(side=tk.LEFT)
            self.buttons.append(button)

        # Create the grid on the canvas
        for row in range(ROWS):
            for col in range(COLUMNS):
                self.canvas.create_oval(col * 100 + 5, row * 100 + 5, col * 100 + 95, row * 100 + 95, fill="white")

    def update_board_gui(self):
        # Update the board based on the board state
        for row in range(ROWS):
            for col in range(COLUMNS):
                color = "white"
                if self.board[row][col] == PLAYER_PIECE:
                    color = "red"
                elif self.board[row][col] == AI_PIECE:
                    color = "yellow"
                self.canvas.create_oval(col * 100 + 5, row * 100 + 5, col * 100 + 95, row * 100 + 95, fill=color)

    def player_move(self, col):
        if is_valid_column(self.board, col):
            row = get_next_open_row(self.board, col)
            drop_piece(self.board, row, col, PLAYER_PIECE)
            self.update_board_gui()

            if check_win(self.board, PLAYER_PIECE):
                messagebox.showinfo("Game Over", "Player wins!")
                self.root.quit()

            # AI's move
            self.root.after(1000, self.ai_move)

    def ai_move(self):
        col, minimax_score = minimax(self.board, MAX_DEPTH, -math.inf, math.inf, True)
        if is_valid_column(self.board, col):
            row = get_next_open_row(self.board, col)
            drop_piece(self.board, row, col, AI_PIECE)
            self.update_board_gui()

            if check_win(self.board, AI_PIECE):
                messagebox.showinfo("Game Over", "AI wins!")
                self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    game = ConnectFourGUI(root)
    root.mainloop()
