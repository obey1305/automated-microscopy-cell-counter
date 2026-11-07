"""Run pretrained Cellpose on a sample image; save local masks and preview."""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
os.environ['CELLPOSE_LOCAL_MODELS_PATH'] = str(ROOT / '.cellpose/models')

import hashlib
import importlib.metadata
import json
import logging
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import tifffile
import torch
from cellpose import models, utils


def main():
    logging.basicConfig(level=logging.INFO)
    source = ROOT / 'data/raw/Fluo-N2DH-GOWT1/Fluo-N2DH-GOWT1/01/t021.tif'
    image = tifffile.imread(source)
    if image.ndim != 2:
        raise ValueError(f'Expected grayscale image, got {image.shape}')
    output = ROOT / 'results/day49'
    output.mkdir(parents=True, exist_ok=True)
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f'Image: {source.name}, {image.shape}; device: {device}', flush=True)
    model = models.CellposeModel(pretrained_model='cpsam_v2', device=device, use_bfloat16=False)
    parameters = dict(batch_size=1, normalize=True, flow_threshold=0.4,
                      cellprob_threshold=0.0, min_size=15)
    started = time.perf_counter()
    masks, flows, styles = model.eval(image, **parameters)
    elapsed = time.perf_counter() - started
    assert masks.shape == image.shape and np.issubdtype(masks.dtype, np.integer)
    count = int(np.unique(masks[masks > 0]).size)
    tifffile.imwrite(output / 'sample_masks.tif', masks.astype(np.uint32))
    outlines = utils.masks_to_outlines(masks)
    overlay = np.repeat((image.astype(np.float32) / 255)[..., None], 3, axis=-1)
    overlay[outlines] = (1, 0.25, 0)
    fig, axes = plt.subplots(1, 2, figsize=(11, 6), layout='constrained')
    axes[0].imshow(image, cmap='gray', vmin=0, vmax=255)
    axes[0].set_title('Raw image · sequence 01 / t021.tif')
    axes[1].imshow(overlay)
    axes[1].set_title(f'Pretrained cpsam_v2 · {count} predicted objects')
    for axis in axes:
        axis.set_axis_off()
    fig.suptitle('Day 49 · Cellpose pretrained inference\nFluo-N2DH-GOWT1 · Cell Tracking Challenge')
    fig.savefig(output / 'segmentation_preview.png', dpi=160, facecolor='white')
    plt.close(fig)
    report = dict(image=str(source.relative_to(ROOT)), image_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  model='cpsam_v2', cellpose_version=importlib.metadata.version('cellpose'),
                  device=str(device), use_bfloat16=False, image_shape=list(image.shape),
                  parameters=parameters, predicted_objects=count, inference_seconds=round(elapsed, 2),
                  note='Predicted nuclear objects, not a validated total cell count. No accuracy evaluation performed.')
    (output / 'run_summary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2), flush=True)
    print(f'Saved outputs to {output}', flush=True)


if __name__ == '__main__':
    main()
