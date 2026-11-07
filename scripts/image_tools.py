"""Decode 2D microscopy uploads and render numbered instance outlines."""
import io
import numpy as np
import tifffile
from PIL import Image, ImageDraw
from cellpose import utils
from scripts.cell_analysis import count_cells


def load_image(data: bytes, filename: str) -> np.ndarray:
    if len(data) > 32 * 1024 * 1024:
        raise ValueError('Use a file smaller than 32 MiB.')
    if filename.lower().endswith(('.tif', '.tiff')):
        with tifffile.TiffFile(io.BytesIO(data)) as tif:
            if len(tif.series) != 1 or len(tif.pages) != 1:
                raise ValueError('Upload one 2D image, not a TIFF stack or multiple series.')
            page = tif.pages[0]
            if page.imagewidth > 4096 or page.imagelength > 4096:
                raise ValueError('Use an image no larger than 4096 × 4096 pixels.')
            image = tif.asarray()
            if page.photometric.name == 'RGB' and page.planarconfig == 2:
                image = np.moveaxis(image, 0, -1)
            if page.photometric.name == 'RGB' and image.ndim == 3 and image.shape[-1] == 4:
                image = image[..., :3]
    else:
        with Image.open(io.BytesIO(data)) as source:
            if source.width > 4096 or source.height > 4096:
                raise ValueError('Use an image no larger than 4096 × 4096 pixels.')
            if source.mode == '1':
                source = source.convert('L')
            if source.mode in ('P', 'RGBA', 'LA', 'CMYK'):
                source = source.convert('RGB')
            image = np.array(source)
    if image.dtype == np.bool_:
        image = image.astype(np.uint8) * 255
    if not (image.ndim == 2 or (image.ndim == 3 and image.shape[-1] == 3)):
        raise ValueError('Use a single grayscale or RGB image; stacks and volumes are not supported.')
    if not np.issubdtype(image.dtype, np.number) or not np.isfinite(image).all() or not image.size:
        raise ValueError('Image must contain finite numeric pixels.')
    if image.shape[0] > 4096 or image.shape[1] > 4096:
        raise ValueError('Use an image no larger than 4096 × 4096 pixels.')
    return image


def display_rgb(image: np.ndarray) -> np.ndarray:
    """Use full uint8 range, or linear full-image range for higher bit depth."""
    pixels = image.astype(np.float32)
    if image.dtype != np.uint8:
        low, high = float(pixels.min()), float(pixels.max())
        pixels = (pixels - low) * (255 / (high - low)) if high > low else np.zeros_like(pixels)
    rgb = np.clip(pixels, 0, 255).astype(np.uint8)
    return np.repeat(rgb[..., None], 3, axis=-1) if rgb.ndim == 2 else rgb


def numbered_overlay(image: np.ndarray, masks: np.ndarray):
    count_cells(masks)
    if image.shape[:2] != masks.shape:
        raise ValueError('Image and mask dimensions must match.')
    rgb = display_rgb(image).copy()
    rgb[utils.masks_to_outlines(masks)] = (255, 100, 0)
    canvas = Image.fromarray(rgb)
    draw = ImageDraw.Draw(canvas)
    positions = []
    for label in np.unique(masks[masks > 0]):
        y, x = np.nonzero(masks == label)
        nearest = np.argmin((y - y.mean()) ** 2 + (x - x.mean()) ** 2)
        px, py = int(x[nearest]), int(y[nearest])
        draw.text((px, py), str(int(label)), fill='cyan', anchor='mm',
                  font_size=max(12, min(24, image.shape[0] // 60)), stroke_width=1, stroke_fill='black')
        positions.append(dict(id=int(label), x=px, y=py))
    return np.array(canvas), positions
