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
