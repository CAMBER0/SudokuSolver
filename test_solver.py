import unittest

from solver import (
    find_pointing_pair,
    apply_eliminations,
    find_claiming_pair,
    find_naked_group,
    apply_naked_eliminations
)

class TestNakedGroups(unittest.TestCase):

    def test_naked_pair(self):
        candidates = {
            (0, 0): {2, 7},
            (0, 3): {2, 7},
            (0, 5): {1, 2, 7, 9},
            (0, 7): {3, 7, 8}
        }

        result = find_naked_group(candidates, 2)

        self.assertIsNotNone(result)
        self.assertEqual(result["strategy"], "Naked Pair")
        self.assertEqual(result["numbers"], {2, 7})

        apply_naked_eliminations(candidates, result)

        self.assertEqual(candidates[(0, 5)], {1, 9})
        self.assertEqual(candidates[(0, 7)], {3, 8})

        # Source cells must not change
        self.assertEqual(candidates[(0, 0)], {2, 7})
        self.assertEqual(candidates[(0, 3)], {2, 7})

    def test_naked_triple(self):
        candidates = {
            (0, 0): {2, 5},
            (0, 3): {2, 5, 8},
            (0, 6): {5, 8},
            (0, 8): {1, 2, 5, 8, 9}
        }

        result = find_naked_group(candidates, 3)

        self.assertIsNotNone(result)
        self.assertEqual(result["strategy"], "Naked Triple")
        self.assertEqual(result["numbers"], {2, 5, 8})

        apply_naked_eliminations(candidates, result)

        self.assertEqual(candidates[(0, 8)], {1, 9})

        # Source cells remain unchanged
        self.assertEqual(candidates[(0, 0)], {2, 5})
        self.assertEqual(candidates[(0, 3)], {2, 5, 8})
        self.assertEqual(candidates[(0, 6)], {5, 8})


class TestPointingPairs(unittest.TestCase):

    def test_pointing_pair_row(self):

        candidates = {
            (0, 0): {1, 5},
            (0, 1): {2, 5},
            (0, 3): {3, 5},
            (0, 6): {4, 5},
        }
        board = [[0] * 9 for _ in range(9)]

        result = find_pointing_pair(candidates, board)

        self.assertIsNotNone(result)
        self.assertEqual(result["number"], 5)
        self.assertEqual(result["direction"], "row")

        apply_eliminations(candidates, result)

        self.assertEqual(candidates[(0, 3)], {3})
        self.assertEqual(candidates[(0, 6)], {4})

        self.assertIn(5, candidates[(0, 0)])
        self.assertIn(5, candidates[(0, 1)])

    def test_pointing_triple_row(self):
        candidates = {
            (1, 0): {2, 7},
            (1, 1): {3, 7},
            (1, 2): {4, 7},

            (1, 4): {5, 7},
            (1, 7): {6, 7}
        }

        board = [[0] * 9 for _ in range(9)]

        result = find_pointing_pair(candidates, board)

        self.assertIsNotNone(result)
        print("Pointing result:", result)
        self.assertEqual(result["strategy"], "Pointing Triple")
        self.assertEqual(result["number"], 7)
        self.assertEqual(result["direction"], "row")

        apply_eliminations(candidates, result)

        self.assertEqual(candidates[(1, 4)], {5})
        self.assertEqual(candidates[(1, 7)], {6})

        # The three source cells should be unchanged
        for col in range(3):
            self.assertIn(7, candidates[(1, col)])

    
    def test_claiming_pair_row(self):
        board = [[0] * 9 for _ in range(9)]

        candidates = {
            (0, 0): {2, 6},
            (0, 1): {3, 6},

            # Candidate 6s elsewhere in the box
            (1, 0): {4, 6},
            (2, 1): {5, 6}
        }

        result = find_claiming_pair(candidates, board)

        self.assertIsNotNone(result)
        self.assertEqual(result["strategy"], "Claiming Pair")
        self.assertEqual(result["number"], 6)
        self.assertEqual(result["direction"], "row")

        apply_eliminations(candidates, result)

        self.assertEqual(candidates[(1, 0)], {4})
        self.assertEqual(candidates[(2, 1)], {5})

        self.assertIn(6, candidates[(0, 0)])
        self.assertIn(6, candidates[(0, 1)])

    def test_claiming_triple_column(self):
        board = [[0] * 9 for _ in range(9)]

        candidates = {
            # Three positions for 8 in column 4
            (0, 3): {1, 8},
            (1, 3): {2, 8},
            (2, 3): {3, 8},

            # Additional candidate 8s in other columns
            # Prevent earlier row-based claiming pairs
            (0, 7): {4, 8},
            (1, 7): {5, 8},
            (2, 7): {6, 8},

            # Candidates elsewhere in the source box
            (0, 4): {7, 8},
            (1, 5): {4, 8},
            (2, 5): {5, 8}
        }

        result = find_claiming_pair(candidates, board)

        self.assertIsNotNone(result)
        self.assertEqual(result["strategy"], "Claiming Triple")
        self.assertEqual(result["number"], 8)
        self.assertEqual(result["direction"], "column")

        apply_eliminations(candidates, result)

        # Candidate 8 should be removed from the box
        self.assertEqual(candidates[(0, 4)], {7})
        self.assertEqual(candidates[(1, 5)], {4})
        self.assertEqual(candidates[(2, 5)], {5})

        # The original three source cells keep 8
        for row in range(3):
            self.assertIn(8, candidates[(row, 3)])

        # Candidates outside the source box remain unchanged
        for row in range(3):
            self.assertIn(8, candidates[(row, 7)])


if __name__ == "__main__":
    unittest.main()
