from solver import solve_logically, get_all_candidates, find_naked_single, find_hidden_single, find_pointing_pair, apply_move, is_valid

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


print("R5C5 board value:", board[4][4])
print("Is 5 valid at R5C5?", is_valid(board, 4, 4, 5))

candidates = get_all_candidates(board)

print("R5C5 candidates:", candidates.get((4, 4)))
solved = solve_logically(board)

print("\nFinal board:")

for row in board:
    print(row)

if solved:
    print("\nPuzzle solved!")
else:
    print("\nNo more basic logical moves found.")