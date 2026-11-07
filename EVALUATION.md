# Day 57 evaluation

Model: Cellpose `cpsam_v2`. Three selected training frames; exploratory evaluation, not held-out validation.

## Method

- Counting reference: number of distinct positive gold tracking marker IDs in the matching `*_GT/TRA/man_trackNNN.tif` frame. These are reference annotations, not a claim of perfect biological counts.
- Segmentation: for each annotated gold segmentation object, find the predicted object with greatest intersection-over-union (IoU). Average these scores, including zero for an unmatched object. Predictions outside annotated objects are not treated as known false positives. This metric does not enforce one-to-one matching and is not official CTC SEG, detection precision, or whole-image pixel accuracy.
- Report raw inference and the previously chosen demonstration filter (minimum area 1,000 pixels, exclude border objects, no maximum) separately.
- Aggregate count MAE/MAPE equally across images. Aggregate IoU weighted by the number of annotated segmentation objects.

## Results

| Image | Stage | Reference count | Predicted count | Absolute count error | Mean best GT IoU |
|---|---|---:|---:|---:|---:|
| 01/t021.tif | raw | 24 | 26 | 2 | 0.9280 |
| 01/t021.tif | filtered | 24 | 22 | 2 | 0.8638 |
| 01/t031.tif | raw | 24 | 26 | 2 | 0.9313 |
| 01/t031.tif | filtered | 24 | 25 | 1 | 0.9313 |
| 02/t001.tif | raw | 25 | 26 | 1 | 0.9355 |
| 02/t001.tif | filtered | 25 | 24 | 1 | 0.9355 |

| Stage | Count MAE (objects/image) | Count MAPE | Mean best GT IoU |
|---|---:|---:|---:|
| raw | 1.667 | 6.89% | 0.9315 |
| filtered | 1.333 | 5.50% | 0.9095 |

## Interpretation and limits

The area/border filter slightly reduces aggregate count error but lowers segmentation overlap because it removes annotated objects on `01/t021.tif` (24 annotated objects reach IoU ≥ 0.5 before filtering, 22 afterward). Thus small objects cannot automatically be assumed to be artifacts. Review thresholds visually; the app defaults to no additional area/border exclusions.

Only three selected images were evaluated, with two frames from the same sequence. The size threshold was previously selected on one of these images; results are not an unbiased estimate of generalization. Pretrained model training overlap with this dataset is unknown. Gold segmentation annotations can be incomplete: `02/t001.tif` has 22 segmented objects but 25 tracking markers. No accuracy claims are made for unannotated objects. A full validation study needs an independent annotated set and documented inclusion rules.

## Reproduce

Run `python scripts/evaluate_day57.py` from the active environment after Days 47 and 49. It reuses the Day 49 prediction for `01/t021.tif` and infers the other two frames. Raw prediction masks, per-object CSVs, `evaluation.csv`, and `evaluation.json` are saved locally in `results/day56_57/`. Source imagery and masks are not redistributed.

Reference annotation documentation: https://celltrackingchallenge.net/annotations/
Official evaluation methodology (distinct from the exploratory metric above): https://celltrackingchallenge.net/evaluation-methodology/
