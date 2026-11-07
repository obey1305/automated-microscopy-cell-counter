import csv
import io
import unittest
import numpy as np
from scripts.reporting import export_cells_csv, evaluate_predictions


class ReportingTests(unittest.TestCase):
    def test_csv_contains_counts_area_and_filter_status_even_when_empty(self):
        rows = list(csv.DictReader(io.StringIO(export_cells_csv('sample.tif',
            [{'id': 7, 'area_pixels': 12, 'kept': False, 'reasons': ['too_small']}], 1, 0))))
        self.assertEqual(rows[0]['area_pixels'], '12')
        self.assertEqual(rows[0]['detected_count'], '1')
        self.assertEqual(rows[0]['retained_count'], '0')
        self.assertIn('area_pixels', export_cells_csv('empty.tif', [], 0, 0))

    def test_perfect_segmentation_ignores_label_numbers(self):
        gt = np.array([[0, 2], [0, 2]])
        pred = np.array([[0, 19], [0, 19]])
        result = evaluate_predictions(pred, gt, reference_count=1)
        self.assertEqual(result['mean_best_gt_iou'], 1)
        self.assertEqual(result['absolute_count_error'], 0)

    def test_missing_object_scores_zero_and_count_error_is_signed(self):
        result = evaluate_predictions(np.zeros((2, 2), dtype=int), np.array([[0, 2], [0, 2]]), 2)
        self.assertEqual(result['mean_best_gt_iou'], 0)
        self.assertEqual(result['signed_count_error'], -2)
        self.assertEqual(result['absolute_percentage_count_error'], 100)
