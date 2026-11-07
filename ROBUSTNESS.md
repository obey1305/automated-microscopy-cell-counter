# Days 58–59: robustness checks

## Executed inference cases

| Case | Reference count | Detected | Absolute error | Mean best annotated-object IoU |
|---|---:|---:|---:|---:|
| real_cluster_crop | 14 | 12 | 2 | 0.942 |
| real_touching_crop | 8 | 8 | 0 | 0.929 |
| real_low_contrast_derived | 25 | 22 | 3 | 0.843 |
| crowded | 36 | 36 | 0 | 0.969 |
| overlapping | 18 | 18 | 0 | 0.820 |
| low_contrast | 36 | 36 | 0 | 0.974 |

Real inputs derive from sequence 02/frame 001: a fixed central cluster crop, a crop with visibly touching nuclei, and a full-frame low-contrast perturbation (intensity × 0.12 + 100, Gaussian noise σ=1.5, seed 59). These are related images, not independent observations. Crop counts use visible tracking-marker IDs, which can omit a clipped object whose marker is outside the crop. Partial segmentation masks restrict overlap evaluation to annotated objects.

Generated fields use fixed seed 58 and designed instance labels: 36 crowded objects, 18 overlapping objects, and 36 low-contrast objects. Counts match, but overlap has lower boundary IoU. The synthetic overlap reference describes visible composited regions, not hidden biological boundaries. These tests exercise the pipeline and are not biological accuracy validation.

## Robustness improvements

- Normalize planar RGB TIFF layout to channel-last.
- Accept 1-bit PNG/TIFF as 0–255 grayscale.
- Convert palette, alpha and CMYK raster inputs to RGB.
- Reject files above 32 MiB and dimensions above 4096 × 4096; inspect dimensions before decoding large raster data.
- Reject stacks, non-finite pixels and unsupported shapes with a clear error.
- Warn on constant-intensity images; preserve original pixels for inference.
- Automated tests cover these regressions, existing counts/areas, CSV generation, and numbered labels.

The public demonstration uses generated input only. Real imagery/results stay local under `results/`. See README and EVALUATION for scope and limitations.
