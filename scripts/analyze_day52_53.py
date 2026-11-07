"""Measure object areas and demonstrate configurable artifact filters."""
import argparse
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from cellpose import utils
from cell_analysis import count_cells, filter_cells

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--min-area', type=int, default=1000, help='Minimum retained area in pixels (inclusive)')
    parser.add_argument('--max-area', type=int, default=None, help='Optional maximum retained area in pixels')
    parser.add_argument('--exclude-border', action='store_true', help='Exclude objects touching the image edge')
    args = parser.parse_args()
    masks = tifffile.imread(ROOT / 'results/day49/sample_masks.tif')
    image = tifffile.imread(ROOT / 'data/raw/Fluo-N2DH-GOWT1/Fluo-N2DH-GOWT1/01/t021.tif')
    filtered, records = filter_cells(masks, args.min_area, args.max_area, args.exclude_border)
    output = ROOT / 'results/day52_53'
    output.mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(output / 'filtered_masks.tif', filtered.astype(np.uint32))
    with (output / 'cell_areas.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'area_pixels', 'touches_border', 'kept', 'reasons'])
        writer.writeheader()
        writer.writerows({**r, 'reasons': ';'.join(r['reasons'])} for r in records)
    summary = dict(original_count=count_cells(masks), retained_count=count_cells(filtered),
                   excluded_count=sum(not r['kept'] for r in records),
                   min_area_pixels=args.min_area, max_area_pixels=args.max_area,
                   exclude_border=args.exclude_border, objects=records,
                   note='Nuclear instance areas in pixels; artifact rules are unvalidated heuristics.')
    (output / 'filter_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    fig, axes = plt.subplots(1, 2, figsize=(13, 7))
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.13, top=0.87, wspace=0.08)
    for ax, labels, title in zip(axes, (masks, filtered),
                                (f'Before: {count_cells(masks)} objects', f'After: {count_cells(filtered)} retained objects')):
        rgb = np.repeat((image.astype(np.float32) / 255)[..., None], 3, axis=-1)
        rgb[utils.masks_to_outlines(labels)] = (1, 0.4, 0)
        ax.imshow(rgb)
        for r in records:
            if r['id'] not in labels:
                continue
            y, x = np.nonzero(labels == r['id'])
            ax.text(x.mean(), y.mean(), str(r['id']), color='cyan', fontsize=8, ha='center', va='center')
        ax.set_title(title)
        ax.set_axis_off()
    fig.suptitle('Days 52–53 · Pixel areas and object filtering', fontsize=17)
    fig.text(0.5, 0.04, f'Min area: {args.min_area} px | Max area: {args.max_area} | Exclude border: {args.exclude_border}\n'
             'Cell Tracking Challenge · Fluo-N2DH-GOWT1 · Original IDs preserved; filters require validation', ha='center', fontsize=10)
    fig.savefig(output / 'filter_comparison.png', dpi=160, facecolor='white')
    plt.close(fig)
    print(f"Original: {summary['original_count']}; retained: {summary['retained_count']}; excluded: {summary['excluded_count']}")
    print('Excluded:', [(r['id'], r['area_pixels'], r['reasons']) for r in records if not r['kept']])
    print(f'Saved measurements, filtered mask, and preview to {output}')


if __name__ == '__main__':
    main()
