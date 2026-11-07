import unittest
import numpy as np
from scripts.cell_analysis import count_cells


class CountCellsTests(unittest.TestCase):
    def test_counts_objects_with_nonconsecutive_ids(self):
        mask = np.array([[0, 4, 4], [19, 0, 19]], dtype=np.uint32)
        self.assertEqual(count_cells(mask), 2)

    def test_background_only_has_no_cells(self):
        self.assertEqual(count_cells(np.zeros((3, 3), dtype=np.uint32)), 0)

    def test_no_background_still_counts_all_objects(self):
        self.assertEqual(count_cells(np.array([[3, 3], [7, 7]])), 2)

    def test_rejects_invalid_label_masks(self):
        for mask in (np.array([[0.0, 1.5]]), np.array([[-1, 0]]), np.zeros((2, 2, 3), dtype=int)):
            with self.subTest(mask=mask):
                with self.assertRaises(ValueError):
                    count_cells(mask)


if __name__ == '__main__':
    unittest.main()
