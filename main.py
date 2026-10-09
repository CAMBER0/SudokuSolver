from solver import get_all_candidates, find_naked_single

board = [
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

candidates = get_all_candidates(board)

for (row, col), nums in sorted(candidates.items()):
    print(
        f"Row {row + 1}, column {col + 1}: "
        f"{sorted(nums)}"
    )


move = find_naked_single(candidates)

if move is not None:
    row, col, number = move

    print(
        f"\nNaked single found: "
        f"Place {number} at "
        f"row {row + 1}, column {col + 1}"
    )
else:
    print("\nNo naked singles found.")
