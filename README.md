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
