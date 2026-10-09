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
            number = next(iter(numbers))
            return row, col, number

    return None

def find_hidden_single(candidates, board):

    units = []

    for row in range(9):
        units.append((
            "row",
            [(row, col) for col in range(9)]
        ))

    for col in range(9):
        units.append((
            "column",
            [(row, col) for row in range(9)]
        ))

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            cells = []

            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    cells.append((row, col))

            units.append(("box", cells))

    for unit_type, cells in units:
        placed_numbers = {
            board[r][c]
            for r, c in cells
            if board[r][c] != 0
        }

        for number in range(1, 10):
            if number in placed_numbers:
                continue

            possible_cells = [
                (r, c)
                for r, c in cells
                if number in candidates.get((r, c), set())
            ]

            if len(possible_cells) == 1:
                r, c = possible_cells[0]
                return r, c, number, unit_type

    return None

def apply_move(board, candidates, row, col, number):

    if board[row][col] != 0:
        raise ValueError("Cell is already filled")

    if number not in candidates.get((row, col), set()):
        raise ValueError(
            f"Invalid placement at R{row + 1}C{col + 1}: "
            f"Trying to place {number}, but candidates are "
            f"{sorted(candidates.get((row, col), set()))}"
        )

    if not is_valid(board, row, col, number):
        raise ValueError("Invalid Sudoku move")

    board[row][col] = number

    del candidates[(row, col)]

    for (r, c), numbers in candidates.items():
        same_row = r == row
        same_col = c == col
        same_box = (
            r // 3 == row // 3
            and c // 3 == col // 3
        )

        if same_row or same_col or same_box:
            numbers.discard(number)


def solve_logically(board):

    candidates = get_all_candidates(board)
    steps = 0

    while True:

        if not candidates:
            return True

        if any(len(nums) == 0 for nums in candidates.values()):
            print("Contradiction: an empty cell has no candidates.")
            return False

        naked = find_naked_single(candidates)

        if naked is not None:
            row, col, number = naked

            print(
                f"Attempting naked single: "
                f"{number} at R{row + 1}C{col + 1}"
            )
            apply_move(board, candidates, row, col, number)
            
            steps += 1

            print(
                f"Step {steps}: Naked single: "
                f"Place {number} at R{row+1}C{col+1}"
            )
            continue

        hidden = find_hidden_single(candidates, board)

        if hidden is not None:
            row, col, number, unit = hidden

            print(
                f"Attempting hidden single ({unit}): "
                f"{number} at R{row + 1}C{col + 1}"
            )

            apply_move(board, candidates, row, col, number)
            steps += 1

            print(
                f"Step {steps}: Hidden single ({unit}): "
                f"Place {number} at R{row+1}C{col+1}"
            )
            continue

        pointing = find_pointing_pair(candidates, board)

        if pointing is not None:

            print(
                f"Pointing {pointing['direction']}: "
                f"number {pointing['number']}, "
                f"source {pointing['source']}, "
                f"eliminations {pointing['eliminations']}"
            )
            apply_eliminations(candidates, pointing)
            steps += 1

            print(
                f"Step {steps}: {pointing['strategy']} "
                f"for number {pointing['number']} "
                f"({pointing['direction']})"
            )

            source = [
                f"R{r+1}C{c+1}"
                for r, c in pointing["source"]
            ]

            removed = [
                f"R{r+1}C{c+1}"
                for r, c in pointing["eliminations"]
            ]

            print(f"  Source cells: {', '.join(source)}")
            print(f"  Eliminated from: {', '.join(removed)}")
            continue

        print(f"\nNo further logical moves after {steps} steps.")
        return False

def find_pointing_pair(candidates, board):
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):

            for number in range(1, 10):
                already_placed = False

                for r in range(box_row, box_row + 3):
                    for c in range(box_col, box_col + 3):
                        if board[r][c] == number:
                            already_placed = True

                if already_placed:
                    continue

                possible_cells = []

                for row in range(box_row, box_row + 3):
                    for col in range(box_col, box_col + 3):
                        if number in candidates.get(
                            (row, col), set()
                        ):
                            possible_cells.append((row, col))

                if not 2 <= len(possible_cells) <= 3:
                    continue

                rows = {r for r, c in possible_cells}

                if len(rows) == 1:
                    row = next(iter(rows))
                    eliminations = []

                    for col in range(9):
                        if box_col <= col < box_col + 3:
                            continue

                        if number in candidates.get(
                            (row, col), set()
                        ):
                            eliminations.append((row, col))

                    if eliminations:
                        return {
                            "strategy": (
                                "Pointing Triple"
                                if len(possible_cells) == 3
                                else "Pointing Pair"
                            ),
                            "number": number,
                            "direction": "row",
                            "source": possible_cells,
                            "eliminations": eliminations
                        }

                cols = {c for r, c in possible_cells}

                if len(cols) == 1:
                    col = next(iter(cols))
                    eliminations = []

                    for row in range(9):
                        if box_row <= row < box_row + 3:
                            continue

                        if number in candidates.get(
                            (row, col), set()
                        ):
                            eliminations.append((row, col))

                    if eliminations:
                        return {
                            "strategy": (
                                "Pointing Triple"
                                if len(possible_cells) == 3
                                else "Pointing Pair"
                            ),
                            "number": number,
                            "direction": "column",
                            "source": possible_cells,
                            "eliminations": eliminations
                        }


    return None

def apply_eliminations(candidates, result):
    number = result["number"]

    for row, col in result["eliminations"]:
        candidates[(row, col)].discard(number)
    