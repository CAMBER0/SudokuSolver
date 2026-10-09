def find_empty(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return row, col  

    return None

def is_valid(board, row, col, number):

    if board[row][col] != 0:
        return False

    for c in range(9):
        if board[row][c] == number:
            return False

    for r in range(9):
        if board[r][col] == number:
            return False

    start_row = (row // 3) * 3
    start_col = (col // 3) * 3

    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if board[r][c] == number:
                return False

    return True


def solve(board):
    empty = find_empty(board)

    if empty is None:
        return True

    row, col = empty

    for number in range(1, 10):
        if is_valid(board, row, col, number):
            board[row][col] = number

            if solve(board):
                return True

            board[row][col] = 0

    return False

def get_candidates(board, row, col):

    if board[row][col] != 0:
        return set()

    candidates = set()

    for number in range(1, 10):
        if is_valid(board, row, col, number):
            candidates.add(number)

    return candidates

def get_all_candidates(board):
    candidates = {}
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                candidates[(row, col)] = get_candidates(
                    board, row, col
                )

    return candidates

def find_naked_single(candidates):
    for (row, col), numbers in sorted(candidates.items()):
        if len(numbers) == 1:
            return row, col, numbers.pop()

    return None

def find_hidden_single(candidates):

    for row in range(9):
        for number in range(1,10):
            possible_cells = []

            for col in range(9):
                if number in candidates.get((row, col), set()):
                    possible_cells.append((row, col))

            if len(possible_cells) == 1:
                r, c = possible_cells[0]
                return r, c, number, "row"

    for col in range(9):
        for number in range(1,10):
            possible_cells = []

            for row in range(9):
                if number in candidates.get((row, col), set()):
                    possible_cells.append((row, col))

            if len(possible_cells) == 1:
                r, c = possible_cells[0]
                return r, c, number, "column"

    for box_row in range(0,9,3):
        for box_col in range(0,9,3):
                for number in range(1,10):
                    possible_cells = []

                    for row in range(box_row, box_row + 3):
                        for col in range(box_col, box_col + 3):
                            if number in candidates.get(
                                (row, col), set()
                            ):
                                possible_cells.append((row, col))

                    if len(possible_cells) == 1:
                        r, c = possible_cells[0]
                        return r, c, number, "box"

    return None

def apply_move(board, row, col, number):
    if board[row][col] != 0:
        raise ValueError("Cell is already filled.")

    if not is_valid(board, row, col, number):
        raise ValueError("Invalid Sudoku move.")

    board[row][col] = number

def solve_logically(board):
    while True:
        candidates = get_all_candidates(board)

        naked = find_naked_single(candidates)

        if naked is not None:
            row, col, number = naked
            apply_move(board, row, col, number)

            print(
                f"Naked single: {number} at "
                f"({row + 1}, {col + 1})"
            )
            continue

        hidden = find_hidden_single(candidates)

        if hidden is not None:
            row, col, number, unit = hidden
            apply_move(board, row, col, number)

            print(
                f"Hidden single {unit}: "
                f"{number} at ({row + 1}, {col + 1})"
            )
            continue

        break

    return all(0 not in row for row in board)