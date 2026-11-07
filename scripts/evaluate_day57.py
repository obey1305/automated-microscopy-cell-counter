"""Evaluate three specified images against tracking and segmentation gold references."""
from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[1]
os.environ['CELLPOSE_LOCAL_MODELS_PATH'] = str(ROOT / '.cellpose/models')
import sys
sys.path.insert(0, str(ROOT))
import csv
import json
import numpy as np
import tifffile
import torch
from cellpose import models
from scripts.cell_analysis import count_cells, filter_cells
from scripts.reporting import evaluate_predictions, export_cells_csv


def main():
    data = ROOT / 'data/raw/Fluo-N2DH-GOWT1/Fluo-N2DH-GOWT1'
    output = ROOT / 'results/day56_57'
    output.mkdir(parents=True, exist_ok=True)
    model = None
    rows = []
    for seq, frame in [('01', '021'), ('01', '031'), ('02', '001')]:
        image = tifffile.imread(data / seq / f't{frame}.tif')
        if (seq, frame) == ('01', '021'):
            prediction = tifffile.imread(ROOT / 'results/day49/sample_masks.tif')
        else:
            if model is None:
                device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
                model = models.CellposeModel(pretrained_model='cpsam_v2', device=device, use_bfloat16=False)
            prediction, _, _ = model.eval(image, batch_size=1, normalize=True, min_size=15)
        tifffile.imwrite(output / f'{seq}_{frame}_prediction.tif', prediction.astype(np.uint32))
        gt = tifffile.imread(data / f'{seq}_GT/SEG/man_seg{frame}.tif')
        tracking = tifffile.imread(data / f'{seq}_GT/TRA/man_track{frame}.tif')
        filtered, records = filter_cells(prediction, min_area=1000, exclude_border=True)
        (output / f'{seq}_{frame}_measurements.csv').write_text(export_cells_csv(f'{seq}/t{frame}.tif', records, count_cells(prediction), count_cells(filtered)))
        for stage, masks in [('raw', prediction), ('filtered', filtered)]:
            row = dict(image=f'{seq}/t{frame}.tif', stage=stage,
                       **evaluate_predictions(masks, gt, count_cells(tracking)))
            rows.append(row)
            print(json.dumps(row), flush=True)
    with (output / 'evaluation.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    aggregate = {}
    for stage in ('raw', 'filtered'):
        subset = [r for r in rows if r['stage'] == stage]
        n = sum(r['annotated_segmentation_objects'] for r in subset)
        aggregate[stage] = dict(images=len(subset), count_mae=float(np.mean([r['absolute_count_error'] for r in subset])),
            count_mape=float(np.mean([r['absolute_percentage_count_error'] for r in subset])),
            mean_best_gt_iou=sum(r['mean_best_gt_iou'] * r['annotated_segmentation_objects'] for r in subset) / n)
    report = dict(model='cpsam_v2', raw_min_size=15, filter_min_area=1000, filter_exclude_border=True,
        images=rows, aggregate=aggregate,
        limitations='Three selected training images, not held-out evaluation. Count references are distinct gold tracking markers; segmentation scores cover annotated gold objects only. Not official CTC metrics. Pretrained training overlap unknown; filters previously chosen on image 01/t021.tif.')
    (output / 'evaluation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(aggregate, indent=2), flush=True)


if __name__ == '__main__':
    main()
