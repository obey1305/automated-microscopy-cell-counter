import io
import unittest
import numpy as np
import tifffile
from PIL import Image
from scripts.image_tools import load_image


class UploadRobustnessTests(unittest.TestCase):
    def test_boolean_microscopy_image_is_accepted(self):
        b=io.BytesIO()
        Image.fromarray(np.array([[True, False],[False, True]])).save(b,format='PNG')
        image=load_image(b.getvalue(),'binary.png')
        self.assertEqual(image.dtype,np.uint8)
        self.assertEqual(int(image.max()),255)

    def test_planar_rgb_tiff_becomes_channel_last(self):
        b=io.BytesIO()
        tifffile.imwrite(b,np.zeros((3,10,12),dtype=np.uint8),photometric='rgb',planarconfig='separate')
        self.assertEqual(load_image(b.getvalue(),'rgb.tif').shape,(10,12,3))

    def test_nan_pixels_and_corrupt_data_rejected(self):
        b=io.BytesIO()
        tifffile.imwrite(b,np.array([[float('nan')]],dtype=np.float32))
        with self.assertRaises(ValueError): load_image(b.getvalue(),'nan.tif')
        with self.assertRaises(Exception): load_image(b'not an image','bad.png')
