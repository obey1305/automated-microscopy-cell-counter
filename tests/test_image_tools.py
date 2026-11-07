import io
import unittest
import numpy as np
import tifffile
from scripts.image_tools import load_image, numbered_overlay


class ImageToolsTests(unittest.TestCase):
    def test_loads_16bit_tiff_without_losing_precision(self):
        image = np.array([[0, 1000], [40000, 65535]], dtype=np.uint16)
        data = io.BytesIO()
        tifffile.imwrite(data, image)
        self.assertTrue(np.array_equal(load_image(data.getvalue(), 'sample.tif'), image))

    def test_rejects_image_stacks(self):
        data = io.BytesIO()
        tifffile.imwrite(data, np.zeros((5, 8, 8), dtype=np.uint16), photometric='minisblack')
        with self.assertRaises(ValueError):
            load_image(data.getvalue(), 'stack.tif')

    def test_overlay_has_one_label_per_instance_inside_its_mask(self):
        mask = np.zeros((80, 80), dtype=np.uint32)
        mask[5:25, 5:25] = 4
        mask[40:70, 40:70] = 19
        rendered, positions = numbered_overlay(np.zeros((80, 80), dtype=np.uint8), mask)
        self.assertEqual(rendered.shape, (80, 80, 3))
        self.assertEqual({p['id'] for p in positions}, {4, 19})
        self.assertTrue(all(mask[p['y'], p['x']] == p['id'] for p in positions))
        self.assertTrue(np.any(rendered > 0))
