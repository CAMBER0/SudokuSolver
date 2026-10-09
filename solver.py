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

