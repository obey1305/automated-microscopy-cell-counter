# Automated Microscopy Cell Counter

Project 4 · Days 46–60 · Python, Cellpose, OpenCV, Streamlit

## Objective
Build an application that detects, counts, and measures cells from uploaded microscope images.

## Day 46: environment setup
The repository and isolated Python 3.11 environment are set up. Installed dependencies are recorded in `requirements-lock.txt`.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m pip check
python -c "import numpy, cv2, streamlit; from cellpose import models; print('Imports OK')"
```

OpenCV uses the headless distribution (`opencv-python-headless`), which provides `cv2` without desktop GUI dependencies and is suitable for a Streamlit application. Cellpose also depends on this distribution, avoiding duplicate OpenCV installations.

Cellpose installation guidance: https://cellpose.readthedocs.io/en/latest/installation.html

## Planned deliverables for Days 47–60
- Automated cell detection and counting
- Segmentation visualization
- Cell area measurements
- Downloadable CSV reports
- Interactive microscopy analysis application
- Demonstration

Day 46 covers repository creation and dependency installation only. No segmentation application or pretrained model download is included yet. Cellpose downloads model weights on first model use.

## Day 47: dataset download
Downloaded and verified the Cell Tracking Challenge Fluo-N2DH-GOWT1 training dataset: 184 microscopy frames and 50 gold segmentation masks, plus tracking and silver annotations. See [DATASET.md](DATASET.md) for local paths, source, checksum, limitations, verification, and use conditions. Dataset files are stored locally and excluded from Git.

## Day 48: load and visualize three images

With the environment activated and the Day 47 data downloaded, run:

```bash
python scripts/visualize_day48.py
```

The script loads `01/t000.tif`, `01/t046.tif`, and `02/t000.tif` with tifffile and displays them side by side using Matplotlib. Each panel shows the sequence, filename, and image dimensions. All panels use the same raw 0–255 grayscale range, with no contrast normalization. The result is saved to `results/day48_three_microscopy_images.png`. This day visualizes raw microscopy images; no segmentation or cell counting is performed.

The generated figure contains source imagery and stays local under the ignored `results/` directory. See [DATASET.md](DATASET.md) for attribution and use conditions.

## Day 49: pretrained Cellpose inference

Run in the project environment:

```bash
python scripts/run_day49_cellpose.py
```

The script loads the full 1024 × 1024 sample `01/t021.tif`, downloads the official pretrained `cpsam_v2` weights on first use into `.cellpose/models/`, and runs Cellpose without training. Apple MPS is used when available, otherwise CPU. Model weights are approximately 1.15 GiB; first use requires internet access. Float32 and a batch size of one are used.

Outputs remain local in `results/day49/`:
- `sample_masks.tif`: uint32 instance labels, with zero for background.
- `segmentation_preview.png`: raw image beside orange predicted boundaries.
- `run_summary.json`: input checksum, model/version, parameters, device, runtime, and predicted object count.

The image shows nuclei; predicted objects are not a validated total cell count. This exercise demonstrates inference and does not evaluate accuracy against the dataset annotations. Dataset imagery and model weights are excluded from Git.

Model documentation: https://cellpose.readthedocs.io/en/latest/models.html

Verified local Day 49 run (8 November 2026): Cellpose 4.2.1.1, `cpsam_v2`, Apple MPS; 26 predicted objects on `01/t021.tif`, 13.07 seconds inference (excluding download/model initialization). Saved mask dimensions and label count were checked against the run summary.

## Days 50–51: numbered boundaries and automatic counting

After running Day 49, run:

```bash
python scripts/visualize_day50_51.py
python -m unittest discover -s tests -v
```

Day 50 displays the saved sample segmentation with orange boundaries and cyan identification numbers. IDs are the original positive instance labels in the mask; label positions are inside the corresponding objects. Outputs: `results/day50_51/numbered_cell_boundaries.png` and `results/day50_51/cell_count.json`. The figure and report remain local.

Day 51 adds `count_cells(masks)` in `scripts/cell_analysis.py`, also used by the Day 49 script. It counts distinct positive IDs, excludes background zero, handles gaps in IDs, and includes objects touching image borders. It expects a 2D nonnegative integer instance mask; a binary foreground image does not distinguish individual objects.

Verified sample result: **26 predicted objects, with 26 displayed IDs**. Tests cover gaps in IDs, all-background masks, masks with no background, and invalid input. These are predicted nuclear instances; accuracy and biological cell counts have not been validated.

## Days 52–53: individual areas and artifact filters

```bash
python scripts/analyze_day52_53.py --min-area 1000 --exclude-border
python -m unittest discover -s tests -v
```

`measure_cell_areas(masks)` in `scripts/cell_analysis.py` returns each original instance ID and its pixel count. These are nuclear mask areas in pixels, not calibrated whole-cell areas. `filter_cells(masks, min_area=1000, max_area=None, exclude_border=False)` creates a filtered copy and an audit record for every original object. It supports inclusive minimum/maximum area bounds and optional rejection of edge-touching objects. Rejected labels become zero; retained IDs stay unchanged. Original masks are preserved.

The minimum of 1,000 pixels is a demonstration setting for this sample, not a validated biological cutoff. Border objects can be real partial nuclei; maximum-area rejection can flag potential merged regions but does not prove an artifact. Adjust these controls for each dataset and inspect the results.

Local outputs in `results/day52_53/`:
- `cell_areas.csv`: all original IDs, pixel areas, border status, retention status and exclusion reasons.
- `filtered_masks.tif`: retained instances with original IDs.
- `filter_summary.json`: filter settings, before/after counts and object records.
- `filter_comparison.png`: labeled before/after visualization.

Verified sample run with the command above: **26 original objects → 22 retained**, excluding IDs 7 (910 px, also touching border), 8 (834 px), 11 (745 px), and 12 (444 px). All four are below the chosen minimum. No maximum area was applied. These exclusions are heuristic decisions, not validated false detections. Generated imagery and masks stay local under the ignored `results/` directory.

## Days 54–55: Streamlit upload and numbered outlines

From the repository root:

```bash
source .venv/bin/activate
streamlit run app.py
```

Open the local address printed by Streamlit (normally http://localhost:8501). Upload a PNG, JPEG, or single-image TIFF, or select **Use the local sample image** when the Day 47 dataset is present. Click **Detect cells** to run pretrained `cpsam_v2`. The original and orange outlines with cyan mask IDs appear side by side, with detected/retained/excluded counts and pixel areas.

Use the sidebar to filter by minimum area, optional maximum area, or border contact. Filters reuse the current predictions without rerunning Cellpose. A new image clears the old predictions. The initial minimum is zero to show all model detections; set 1,000 to reproduce the Day 53 sample exclusions. Cellpose itself uses a 15-pixel minimum during inference.

Supported inputs: single 2D grayscale or RGB images up to 4096 × 4096 pixels; TIFF stacks/volumes are rejected with a message. Original higher-bit-depth pixels are retained for inference, with linear min–max scaling used only for preview. uint8 images use their original 0–255 display range. First model use downloads approximately 1.15 GiB of weights; GPU acceleration uses Apple MPS when available, otherwise CPU.

The app runs locally; no hosting deployment is included. Predicted boundaries, counts, filter decisions, and nuclear pixel areas need visual review and are not validated biological measurements.

## Days 56–57: CSV export and reference evaluation

After detection, click **Download counts and measurements (CSV)**. The report contains the source filename, detected and retained counts, all original IDs, pixel areas, retention status, and exclusion reasons. Image-level counts are repeated on each object row; do not sum those count columns. A zero-detection result includes a summary row with blank object fields. Filter changes update the download.

Run `python scripts/evaluate_day57.py` to reproduce the three-image counting and segmentation evaluation. See [EVALUATION.md](EVALUATION.md) for methods, results, and limitations. Both raw and filtered predictions are evaluated. Filtering improved count MAE slightly but removed some annotated objects; thresholds require review. This is exploratory evaluation, not held-out or official CTC benchmark performance.
