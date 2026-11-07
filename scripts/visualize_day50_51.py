"""Display detected boundaries and mask IDs, and count detected objects."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
import tifffile
from cellpose import utils
from cell_analysis import count_cells

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'data/raw/Fluo-N2DH-GOWT1/Fluo-N2DH-GOWT1/01/t021.tif'
    mask_path = ROOT / 'results/day49/sample_masks.tif'
    image = tifffile.imread(source)
    masks = tifffile.imread(mask_path)
    if image.shape != masks.shape:
        raise ValueError('Image and mask dimensions must match')
    count = count_cells(masks)
    overlay = np.repeat((image.astype(np.float32) / 255)[..., None], 3, axis=-1)
    overlay[utils.masks_to_outlines(masks)] = (1, 0.35, 0)
    fig, ax = plt.subplots(figsize=(10, 12))
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.10, top=0.89)
    ax.imshow(overlay)
    objects = []
    for label in np.unique(masks[masks > 0]):
        ys, xs = np.nonzero(masks == label)
        # Pick an actual object pixel nearest its centroid, so IDs stay inside masks.
        nearest = np.argmin((ys - ys.mean()) ** 2 + (xs - xs.mean()) ** 2)
        x, y = int(xs[nearest]), int(ys[nearest])
        ax.text(x, y, str(int(label)), color='cyan', ha='center', va='center',
                fontsize=10, weight='bold', path_effects=[pe.withStroke(linewidth=2, foreground='black')])
        objects.append(dict(id=int(label), label_x=x, label_y=y))
    ax.set_title(f'Days 50–51 · Numbered cell boundaries\nSequence 01 / t021.tif · {count} detected objects', fontsize=16)
    ax.set_axis_off()
    fig.text(0.5, 0.035, 'Orange: predicted boundaries · Cyan: mask IDs\nCell Tracking Challenge · Fluo-N2DH-GOWT1 · Predictions are not validated cell counts',
             ha='center', fontsize=10)
    output = ROOT / 'results/day50_51'
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / 'numbered_cell_boundaries.png', dpi=160, facecolor='white')
    plt.close(fig)
    report = dict(image=str(source.relative_to(ROOT)), mask=str(mask_path.relative_to(ROOT)),
                  detected_cells=count, includes_border_objects=True, objects=objects,
                  note='Counts predicted nuclear instances, not a validated biological cell total.')
    (output / 'cell_count.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Detected objects: {count}; assigned {len(objects)} IDs')
    print(f'Saved figure and count report to {output}')


if __name__ == '__main__':
    main()
