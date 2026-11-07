"""Load three microscopy TIFFs and save a local visualization.

Run from any directory: .venv/bin/python scripts/visualize_day48.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Save without requiring a desktop display.
import matplotlib.pyplot as plt
import numpy as np
import tifffile


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/raw/Fluo-N2DH-GOWT1/Fluo-N2DH-GOWT1"
FRAMES = ("01/t000.tif", "01/t046.tif", "02/t000.tif")
OUTPUT = ROOT / "results/day48_three_microscopy_images.png"


def main():
    images = []
    for frame in FRAMES:
        path = DATA / frame
        if not path.is_file():
            raise FileNotFoundError(f"Missing {path}. Download the dataset using DATASET.md.")
        image = tifffile.imread(path)
        if image.ndim != 2 or image.dtype != np.uint8:
            raise ValueError(f"Expected a 2D uint8 image at {path}; got {image.shape}, {image.dtype}")
        images.append(image)
        print(f"Loaded {frame}: shape={image.shape}, dtype={image.dtype}, range={image.min()}..{image.max()}")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.7), layout="constrained")
    for axis, frame, image in zip(axes, FRAMES, images):
        displayed = axis.imshow(image, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
        sequence, filename = frame.split("/")
        axis.set_title(f"Sequence {sequence} | {filename}\n1024 × 1024 pixels", fontsize=12)
        axis.set_axis_off()
    fig.suptitle("Day 48 · Three microscopy images\nFluo-N2DH-GOWT1 · Cell Tracking Challenge", fontsize=17)
    fig.colorbar(displayed, ax=axes, orientation="horizontal", fraction=0.045, pad=0.03,
                 label="Raw pixel intensity (shared 0–255 grayscale)")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=160, facecolor="white")
    plt.close(fig)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
