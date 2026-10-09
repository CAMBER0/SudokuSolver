import unittest

from solver import (
    find_pointing_pair,
    apply_eliminations
)

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


if __name__ == "__main__":
    unittest.main()
