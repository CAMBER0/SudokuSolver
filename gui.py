import tkinter as tk
from tkinter import messagebox
from solver import solve_logically

EXAMPLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]


def valid_board(board):
    """Check that existing numbers do not break Sudoku rules."""

    if len(board) != 9 or any(len(row) != 9 for row in board):
        return False

    if any(
        not isinstance(n, int) or not 0 <= n <= 9
        for row in board for n in row
    ):
        return False

    units = []

    for i in range(9):
        units.append(board[i])
        units.append([board[r][i] for r in range(9)])

    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            units.append([
                board[r][c]
                for r in range(br, br + 3)
                for c in range(bc, bc + 3)
            ])

    for unit in units:
        numbers = [n for n in unit if n != 0]

        if len(numbers) != len(set(numbers)):
            return False

    return True

def completed_board(board):
    return (
       all(0 not in row for row in board)
       and valid_board(board)
    )

class SudokuApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.root.resizable(False, False)

        self.cells = []

        title = tk.Label(
            root,
            text="Sudoku Solver",
            font=("Helvetica", 16, "bold")
        )
        title.pack(pady=(15,5))

        self.status = tk.StringVar(value="Enter a puzzle to begin.")

        board_frame = tk.Frame(root, bg="black", padx=2, pady=2)
        board_frame.pack(padx=15, pady=10)

        validator = root.register(self.validate_entry)

        for row in range(9):
            cell_row = []

            for col in range(9):

                box_index = (row // 3) * 3 + (col // 3) % 2
                bg = "#FFFFFF" if box_index == 0 else "#E9EEF5"

                padx = (1,4 if col in (2, 5) else 1)
                pady = (1,4 if row in (2, 5) else 1)

                entry = tk.Entry(
                    board_frame,
                    width=2,
                    font=("Helvetica", 16),
                    justify="center",
                    bg=bg,
                    fg="#111827",
                    relief="flat",
                    validate="key",
                    validatecommand=(validator, "%P")
                )

                entry.grid(
                    row=row,
                    column=col,
                    padx=padx,
                    pady=pady,
                    ipady=5
                )

                cell_row.append(entry)

            self.cells.append(cell_row)

        buttons = tk.Frame(root)
        buttons.pack(pady=8)

        tk.Button(
            buttons,
            text="Solve",
            width=11,
            command=self.solve
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            buttons,
            text="Load Example",
            width=13,
            command=self.clear
        ).grid(row=0, column=2, padx=5)

        tk.Label(
            root,
            textvariable=self.status,
            font=("Helvetica", 10),
            wraplength=360,
        ).pack(pady=(5, 15))

    def validate_entry(self, value):
        return value == "" or (len(value) == 1 and value in "123456789")

    def read_board(self):
        
        board = []

        for row in self.cells:
            numbers = []

            for entry in row:
                value = entry.get().strip()
                numbers.append(int(value) if value else 0)

            board.append(numbers)

        return board

    def display_board(self, board, original=None):
        for r in range(9):
            for c in range(9):
                entry = self.cells[r][c]

                entry.delete(0, tk.END)

                if board[r][c] != 0:
                    entry.insert(0, str(board[r][c]))

                if original and original[r][c] == 0:
                    entry.config(fg="#2563EB")
                else:
                    entry.config(fg="#111827")

    def solve(self):
        original = self.read_board()

        if not valid_board(original):
            messagebox.showerror(
                "Invalid Sudoku",
                "The puzzle you entered is invalid. Please check your entries."
            )
            return

        board = [row.copy() for row in original]

        self.status.set("Solving...")
        self.root.update_idletasks()

        try:
            solved = solve_logically(board)
        except (ValueError, KeyError) as error:
            messagebox.showerror(
                "Error",
                str(error)
            )
            self.status.set("An error occurred.")
            return

        if solved and completed_board(board):
            self.display_board(board, original)
            self.status.set("Puzzle solved!")


        elif valid_board(board):
            self.display_board(board, original)

            remaining = sum(
                row.count(0)
                for row in board
            )

            self.status.set(
                f"Partial solution: {remaining} empty cells remain. "
                "Your puzzle requires advanced techniques that are not implemented yet."
            )


        else:
            self.status.set(
                "The solver produced an invalid board"
            )
            messagebox.showerror(
                "Solver Error",
                "The solver produced an invalid board. "
            )

    def clear(self):
        self.display_board([[0] * 9 for _ in range(9)])
        self.status.set("Board cleared.")

    def load_example(self):
        self.display_board(EXAMPLE)
        self.status.set("Example puzzle loaded.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()