from itertools import combinations

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

def find_hidden_group(candidates, board, group_size, target_numbers=None):
    """Find hidden pairs or triples in rows, columns, or boxes."""

    if group_size not in (2, 3):
        raise ValueError("Group size must be 2 or 3")

    units = []

    for row in range(9):
        units.append(("row", [(row, c) for c in range(9)]))

    for col in range(9):
        units.append(("column", [(r, col) for r in range(9)]))

    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            units.append((
                "box",
                [(r, c) for r in range(br, br + 3)
                 for c in range(bc, bc + 3)]
            ))

    for unit_type, cells in units:
        placed = {board[r][c] for r, c in cells}

        number_groups = (
            [tuple(sorted(target_numbers))]
            if target_numbers is not None
            else combinations(range(1, 10), group_size)
        )

        for numbers_tuple in number_groups:
            numbers = set(numbers_tuple)

            # Already placed numbers cannot form a hidden group
            if numbers & placed:
                continue

            positions = {
                number: {
                    cell for cell in cells
                    if number in candidates.get(cell, set())
                }
                for number in numbers
            }

            # Every selected number needs at least one position
            if any(not positions[n] for n in numbers):
                continue

            group_cells = set().union(*positions.values())

            # N numbers restricted to exactly N cells
            if len(group_cells) != group_size:
                continue

            eliminations = []

            for cell in sorted(group_cells):
                for value in sorted(candidates[cell] - numbers):
                    eliminations.append((cell, value))

            if eliminations:
                return {
                    "strategy": (
                        "Hidden Pair" if group_size == 2
                        else "Hidden Triple"
                    ),
                    "unit": unit_type,
                    "source": sorted(group_cells),
                    "numbers": numbers,
                    "eliminations": eliminations
                }

def find_x_wing(candidates, board):
    """Find row-based or column-based X-Wing patterns."""

    for number in range(1, 10):
        for direction in ("row", "column"):

            positions = {}

            # Find units with exactly two candidate positions
            for index in range(9):
                if direction == "row":
                    cells = [(index, c) for c in range(9)]
                else:
                    cells = [(r, index) for r in range(9)]

                # Skip units already containing this number
                if any(board[r][c] == number for r, c in cells):
                    continue

                possible = [
                    c if direction == "row" else r
                    for r, c in cells
                    if number in candidates.get((r, c), set())
                ]

                if len(possible) == 2:
                    positions[index] = tuple(possible)

            # Compare all pairs of rows or columns
            for first, second in combinations(positions, 2):
                if positions[first] != positions[second]:
                    continue

                a, b = positions[first]
                source = []
                eliminations = []

                if direction == "row":
                    source = [
                        (first, a), (first, b),
                        (second, a), (second, b)
                    ]

                    for row in range(9):
                        if row in (first, second):
                            continue

                        for col in (a, b):
                            if number in candidates.get(
                                (row, col), set()
                            ):
                                eliminations.append(
                                    ((row, col), number)
                                )

                else:
                    source = [
                        (a, first), (b, first),
                        (a, second), (b, second)
                    ]

                    for col in range(9):
                        if col in (first, second):
                            continue

                        for row in (a, b):
                            if number in candidates.get(
                                (row, col), set()
                            ):
                                eliminations.append(
                                    ((row, col), number)
                                )

                if eliminations:
                    return {
                        "strategy": "X-Wing",
                        "unit": direction,
                        "source": source,
                        "numbers": {number},
                        "eliminations": eliminations
                    }

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

        claiming = find_claiming_pair(candidates, board)

        if claiming is not None:
            apply_eliminations(candidates, claiming)
            steps += 1

            source = [
                f"R{r+1}C{c+1}"
                for r, c in claiming["source"]
            ]

            removed = [
                f"R{r+1}C{c+1}"
                for r, c in claiming["eliminations"]
            ]

            print(
                f"Step {steps}: {claiming['strategy']} "
                f"for number {claiming['number']}"
            )

            print(f"  Source: {', '.join(source)}")
            print(f"  Eliminated from: {', '.join(removed)}")

            continue

        naked_group = None

        for size in (2, 3):
            naked_group = find_naked_group(candidates, size)

            if naked_group is not None:
                break

        if naked_group is not None:
            apply_naked_eliminations(candidates, naked_group)
            steps += 1

            source = [
                f"R{r+1}C{c+1}"
                for r, c in naked_group["source"]
            ]

            removed = [
                f"{num} from R{cell[0]+1}C{cell[1]+1}"
                for cell, num in naked_group["eliminations"]
            ]

            print(
                f"Step {steps}: {naked_group['strategy']} "
                f"in {naked_group['unit']}"
            )

            print(
                f"  Numbers: "
                f"{sorted(naked_group['numbers'])}"
            )
            print(f"  Source: {', '.join(source)}")
            print(f"  Eliminations: {', '.join(removed)}")

            continue

        hidden_group = None

        for size in (2, 3):
            hidden_group = find_hidden_group(
                candidates, board, size
            )
            if hidden_group is not None:
                break

        if hidden_group is not None:
            apply_naked_eliminations(candidates, hidden_group)
            steps += 1

            print(
                f"Step {steps}: {hidden_group['strategy']} "
                f"in {hidden_group['unit']}"
            )
            print(f"  Numbers: {sorted(hidden_group['numbers'])}")
            print(f"  Source: {hidden_group['source']}")
            print(f"  Eliminations: {hidden_group['eliminations']}")

            continue

        # Strategy 7: X-Wing
        x_wing = find_x_wing(candidates, board)

        if x_wing is not None:
            apply_naked_eliminations(candidates, x_wing)
            steps += 1

            print(
                f"Step {steps}: X-Wing on "
                f"{next(iter(x_wing['numbers']))} "
                f"using {x_wing['unit']}s"
            )
            print(f"  Corners: {x_wing['source']}")
            print(f"  Eliminations: {x_wing['eliminations']}")

            continue

        xy_wing = find_xy_wing(candidates)

        if xy_wing is not None:
            apply_naked_eliminations(candidates, xy_wing)
            steps += 1

            print(f"Step {steps}: XY-Wing")
            print(f"  Cells: {xy_wing['source']}")
            print(f"  Eliminations: {xy_wing['eliminations']}")

            continue

        # Strategy 9: Swordfish
        swordfish = find_swordfish(candidates, board)

        if swordfish is not None:
            apply_naked_eliminations(candidates, swordfish)
            steps += 1

            print(
                f"Step {steps}: Swordfish "
                f"using {swordfish['unit']}s"
            )
            print(f"  Source: {swordfish['source']}")
            print(f"  Eliminations: {swordfish['eliminations']}")

            continue

        # Strategy 10: Jellyfish
        jellyfish = find_jellyfish(candidates, board)

        if jellyfish is not None:
            apply_naked_eliminations(candidates, jellyfish)
            steps += 1

            print(f"Step {steps}: Jellyfish")
            print(f"  Source: {jellyfish['source']}")
            print(f"  Eliminations: {jellyfish['eliminations']}")
            continue

        # Strategy 11: XYZ-Wing
        xyz_wing = find_xyz_wing(candidates)

        if xyz_wing is not None:
            apply_naked_eliminations(candidates, xyz_wing)
            steps += 1

            print(f"Step {steps}: XYZ-Wing")
            print(f"  Source: {xyz_wing['source']}")
            print(f"  Eliminations: {xyz_wing['eliminations']}")
            continue

        # Strategy 12: Skyscraper
        skyscraper = find_skyscraper(candidates, board)

        if skyscraper is not None:
            apply_naked_eliminations(candidates, skyscraper)
            steps += 1

            print(f"Step {steps}: Skyscraper")
            print(f"  Source: {skyscraper['source']}")
            print(f"  Eliminations: {skyscraper['eliminations']}")
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

def find_claiming_pair(candidates, board):

    for direction in ("row", "column"):
        for index in range(9):
            for number in range(1, 10):

                if direction == "row":
                    cells = [(index, c) for c in range(9)]
                else:
                    cells = [(r, index) for r in range(9)]

                if any(board[r][c] == number for r, c in cells):
                    continue

                possible_cells = [
                    (r, c)
                    for r, c in cells
                    if number in candidates.get((r, c), set())
                ]

                if not 2 <= len(possible_cells) <= 3:
                    continue

                boxes = {
                    (r // 3, c // 3)
                    for r, c in possible_cells
                }

                if len(boxes) != 1:
                    continue

                box_r, box_c = next(iter(boxes))

                eliminations = []

                for r in range(box_r * 3, box_r * 3 + 3):
                    for c in range(box_c * 3, box_c * 3 + 3):

                        # Skip cells in the original row/column
                        if (r, c) in cells:
                            continue

                        if number in candidates.get((r, c), set()):
                            eliminations.append((r, c))

                if eliminations:
                    return {
                        "strategy": (
                            "Claiming Pair"
                            if len(possible_cells) == 2
                            else "Claiming Triple"
                        ),
                        "number": number,
                        "direction": direction,
                        "source": possible_cells,
                        "eliminations": eliminations
                    }

    return None

def apply_eliminations(candidates, result):
    number = result["number"]

    for row, col in result["eliminations"]:
        candidates[(row, col)].discard(number)

def find_naked_group(candidates, group_size):

    if group_size not in (2, 3):
        raise ValueError("Group size must be 2 or 3")

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
            units.append((
                "box",
                [
                    (r, c)
                    for r in range(box_row, box_row + 3)
                    for c in range(box_col, box_col + 3)
                ]
            ))

    for unit_type, cells in units:

        eligible = [
            cell for cell in cells
            if 2 <= len(candidates.get(cell, set())) <= group_size
        ]

        for group in combinations(eligible, group_size):

            numbers = set()

            for cell in group:
                numbers.update(candidates[cell])

            if len(numbers) != group_size:
                continue

            other_cells = [
                cell for cell in cells
                if cell in candidates and cell not in group
            ]

            if any(
                candidates[cell] and
                candidates[cell].issubset(numbers)
                for cell in other_cells
            ):
                continue

            eliminations = []

            for cell in other_cells:
                for number in numbers:
                    if number in candidates[cell]:
                        eliminations.append((cell, number))

            if eliminations:
                return {
                    "strategy": (
                        "Naked Pair"
                        if group_size == 2
                        else "Naked Triple"
                    ),
                    "unit": unit_type,
                    "source": list(group),
                    "numbers": numbers,
                    "eliminations": eliminations
                }

    return None

def apply_naked_eliminations(candidates, result):

    for (row, col), number in result["eliminations"]:
        candidates[(row, col)].discard(number)


def can_see(cell1, cell2):
    """Check whether two different cells share a Sudoku unit."""

    if cell1 == cell2:
        return False

    r1, c1 = cell1
    r2, c2 = cell2

    return (
        r1 == r2
        or c1 == c2
        or (r1 // 3 == r2 // 3 and c1 // 3 == c2 // 3)
    )

def find_xy_wing(candidates):
    """Find an XY-Wing and return candidate eliminations."""

    # XY-Wing uses only cells with exactly two candidates
    pairs = {
        cell: nums
        for cell, nums in candidates.items()
        if len(nums) == 2
    }

    for pivot, pivot_nums in pairs.items():

        # Find the two pincers visible to the pivot
        visible = [
            cell for cell in pairs
            if can_see(pivot, cell)
        ]

        for pincer1, pincer2 in combinations(visible, 2):
            nums1 = pairs[pincer1]
            nums2 = pairs[pincer2]

            # Each pincer shares exactly one number
            # with the pivot
            shared1 = nums1 & pivot_nums
            shared2 = nums2 & pivot_nums

            if len(shared1) != 1 or len(shared2) != 1:
                continue

            # The two shared numbers must be different
            if shared1 == shared2:
                continue

            # Both pincers share the third number Z
            z1 = nums1 - pivot_nums
            z2 = nums2 - pivot_nums

            if len(z1) != 1 or z1 != z2:
                continue

            z = next(iter(z1))

            eliminations = []

            for cell, nums in candidates.items():
                if cell in (pivot, pincer1, pincer2):
                    continue

                if (
                    z in nums
                    and can_see(cell, pincer1)
                    and can_see(cell, pincer2)
                ):
                    eliminations.append((cell, z))

            if eliminations:
                return {
                    "strategy": "XY-Wing",
                    "unit": "wing",
                    "source": [pivot, pincer1, pincer2],
                    "numbers": {z},
                    "eliminations": eliminations
                }

    return None

def find_swordfish(candidates, board):
    """Find row-based and column-based Swordfish patterns."""

    for number in range(1, 10):
        for direction in ("row", "column"):

            positions = {}

            # Find rows or columns with 2-3 candidates
            for index in range(9):
                if direction == "row":
                    cells = [(index, c) for c in range(9)]
                else:
                    cells = [(r, index) for r in range(9)]

                # Skip units already containing the number
                if any(board[r][c] == number for r, c in cells):
                    continue

                possible = {
                    c if direction == "row" else r
                    for r, c in cells
                    if number in candidates.get((r, c), set())
                }

                if 2 <= len(possible) <= 3:
                    positions[index] = possible

            # Select three rows or three columns
            for group in combinations(positions, 3):
                cover = set()

                for index in group:
                    cover.update(positions[index])

                # All candidates must occupy exactly
                # three distinct columns or rows
                if len(cover) != 3:
                    continue

                source = []
                eliminations = []

                for index in group:
                    for other in positions[index]:
                        if direction == "row":
                            source.append((index, other))
                        else:
                            source.append((other, index))

                # Remove candidates outside the three
                # base units, inside the three cover units
                for index in range(9):
                    if index in group:
                        continue

                    for other in sorted(cover):
                        cell = (
                            (index, other)
                            if direction == "row"
                            else (other, index)
                        )

                        if number in candidates.get(cell, set()):
                            eliminations.append((cell, number))

                if eliminations:
                    return {
                        "strategy": "Swordfish",
                        "unit": direction,
                        "source": sorted(source),
                        "numbers": {number},
                        "eliminations": eliminations
                    }

    return None

def find_jellyfish(candidates, board):
    """Find row-based and column-based Jellyfish patterns."""

    for number in range(1, 10):
        for direction in ("row", "column"):

            positions = {}

            for index in range(9):
                if direction == "row":
                    cells = [(index, c) for c in range(9)]
                else:
                    cells = [(r, index) for r in range(9)]

                # Ignore units already containing the number
                if any(board[r][c] == number for r, c in cells):
                    continue

                possible = {
                    c if direction == "row" else r
                    for r, c in cells
                    if number in candidates.get((r, c), set())
                }

                if 2 <= len(possible) <= 4:
                    positions[index] = possible

            # Find four base rows or columns
            for group in combinations(positions, 4):
                cover = set()

                for index in group:
                    cover.update(positions[index])

                if len(cover) != 4:
                    continue

                source = []
                eliminations = []

                for index in group:
                    for other in sorted(positions[index]):
                        cell = (
                            (index, other)
                            if direction == "row"
                            else (other, index)
                        )
                        source.append(cell)

                # Eliminate from the cover units
                # outside the four base units
                for index in range(9):
                    if index in group:
                        continue

                    for other in sorted(cover):
                        cell = (
                            (index, other)
                            if direction == "row"
                            else (other, index)
                        )

                        if number in candidates.get(cell, set()):
                            eliminations.append((cell, number))

                if eliminations:
                    return {
                        "strategy": "Jellyfish",
                        "unit": direction,
                        "source": sorted(source),
                        "numbers": {number},
                        "eliminations": eliminations
                    }

    return None

def find_xyz_wing(candidates):
    """Find an XYZ-Wing and return candidate eliminations."""

    pivots = [
        cell for cell, nums in candidates.items()
        if len(nums) == 3
    ]

    pairs = {
        cell: nums
        for cell, nums in candidates.items()
        if len(nums) == 2
    }

    for pivot in pivots:
        pivot_nums = candidates[pivot]

        # Pincers see the pivot and contain
        # only numbers from the pivot
        possible_pincers = [
            cell for cell, nums in pairs.items()
            if can_see(pivot, cell)
            and nums.issubset(pivot_nums)
        ]

        for pincer1, pincer2 in combinations(
            possible_pincers, 2
        ):
            nums1 = pairs[pincer1]
            nums2 = pairs[pincer2]

            common = nums1 & nums2

            # Both pincers share exactly one number
            if len(common) != 1:
                continue

            # Together, pincers cover all pivot numbers
            if nums1 | nums2 != pivot_nums:
                continue

            z = next(iter(common))
            eliminations = []

            for cell, nums in candidates.items():
                if cell in (pivot, pincer1, pincer2):
                    continue

                if (
                    z in nums
                    and can_see(cell, pivot)
                    and can_see(cell, pincer1)
                    and can_see(cell, pincer2)
                ):
                    eliminations.append((cell, z))

            if eliminations:
                return {
                    "strategy": "XYZ-Wing",
                    "unit": "wing",
                    "source": [pivot, pincer1, pincer2],
                    "numbers": {z},
                    "eliminations": eliminations
                }

    return None


def find_skyscraper(candidates, board):
    """Find row-based and column-based skyscrapers."""

    for number in range(1, 10):
        for direction in ("row", "column"):

            strong_links = {}

            for index in range(9):
                if direction == "row":
                    cells = [(index, c) for c in range(9)]
                else:
                    cells = [(r, index) for r in range(9)]

                if any(board[r][c] == number for r, c in cells):
                    continue

                possible = [
                    cell for cell in cells
                    if number in candidates.get(cell, set())
                ]

                if len(possible) == 2:
                    strong_links[index] = possible

            for first, second in combinations(strong_links, 2):
                link1 = strong_links[first]
                link2 = strong_links[second]

                # Try each choice of the base endpoints
                for base1 in link1:
                    for base2 in link2:
                        if not can_see(base1, base2):
                            continue

                        end1 = next(
                            cell for cell in link1
                            if cell != base1
                        )
                        end2 = next(
                            cell for cell in link2
                            if cell != base2
                        )

                        # Opposite endpoints must differ in
                        # their perpendicular coordinates
                        if direction == "row":
                            if end1[1] == end2[1]:
                                continue
                        else:
                            if end1[0] == end2[0]:
                                continue

                        eliminations = []

                        for cell, nums in candidates.items():
                            if cell in (base1, base2, end1, end2):
                                continue

                            if (
                                number in nums
                                and can_see(cell, end1)
                                and can_see(cell, end2)
                            ):
                                eliminations.append((cell, number))

                        if eliminations:
                            return {
                                "strategy": "Skyscraper",
                                "unit": direction,
                                "source": [
                                    base1, base2, end1, end2
                                ],
                                "numbers": {number},
                                "eliminations": eliminations
                            }

    return None