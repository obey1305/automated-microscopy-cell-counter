import unittest
import numpy as np
from scripts.cell_analysis import measure_cell_areas, filter_cells


class MeasurementTests(unittest.TestCase):
    def test_areas_use_pixel_counts_and_original_ids(self):
        m = np.array([[0, 4, 4], [19, 0, 19]])
        self.assertEqual(measure_cell_areas(m), [{'id': 4, 'area_pixels': 2}, {'id': 19, 'area_pixels': 2}])

    def test_empty_mask_has_no_measurements(self):
        self.assertEqual(measure_cell_areas(np.zeros((0, 0), dtype=int)), [])

    def test_filter_limits_are_inclusive_preserve_ids_and_input(self):
        m = np.array([[0, 4, 4, 0], [7, 0, 19, 19], [0, 0, 19, 0]])
        before = m.copy()
        filtered, report = filter_cells(m, min_area=2, max_area=2)
        self.assertEqual(set(np.unique(filtered)), {0, 4})
        self.assertTrue(np.array_equal(m, before))
        self.assertEqual({r['id']: r['reasons'] for r in report}, {4: [], 7: ['too_small'], 19: ['too_large']})

    def test_border_exclusion_is_optional(self):
        m = np.zeros((5, 5), dtype=int)
        m[0, 2] = 8
        m[2, 2] = 15
        filtered, report = filter_cells(m, min_area=1, exclude_border=True)
        self.assertEqual(set(np.unique(filtered)), {0, 15})
        self.assertEqual(report[0]['reasons'], ['touches_border'])
        self.assertEqual(set(np.unique(filter_cells(m, min_area=1)[0])), {0, 8, 15})

    def test_invalid_thresholds_are_rejected(self):
        for kwargs in ({'min_area': -1}, {'min_area': 1.5}, {'min_area': 5, 'max_area': 2}):
            with self.assertRaises(ValueError):
                filter_cells(np.zeros((2, 2), dtype=int), **kwargs)
