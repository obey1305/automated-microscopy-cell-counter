# Day 47: microscopy dataset

Completed: 8 November 2026.

## Downloaded source
- Dataset: Fluo-N2DH-GOWT1, Cell Tracking Challenge training dataset.
- Subject: fluorescence microscopy of GFP-GOWT1 mouse stem-cell nuclei.
- Dataset page: https://celltrackingchallenge.net/2d-datasets/
- Direct archive: https://data.celltrackingchallenge.net/training-datasets/Fluo-N2DH-GOWT1.zip
- Conditions: https://celltrackingchallenge.net/datasets/
- Archive size: 59,331,035 bytes.
- SHA-256: `1a7bd9a7d1d10c4122c7782427b437246fb69cc3322a975485c04e206f64fc2c`.

## Local files
Archive: `data/raw/Fluo-N2DH-GOWT1.zip`.
Extracted root: `data/raw/Fluo-N2DH-GOWT1/Fluo-N2DH-GOWT1/`.

- `01/` and `02/`: 92 raw TIFF frames each (184 total), 1024 × 1024, uint8.
- `01_GT/SEG/`: 30 gold-standard segmentation masks.
- `02_GT/SEG/`: 20 gold-standard segmentation masks.
- `*_GT/TRA/`: tracking annotations; these are not full cell-area segmentation masks.
- `*_ST/`: silver-standard segmentation annotations.
- `*_ERR_SEG/`: imperfect segmentation masks supplied by the source.

The gold segmentation masks are uint16 instance-label images: zero is background and each positive label identifies an annotated nucleus. Many frames contain partial annotations. The number of positive labels is the number of annotated objects, not necessarily the total number of nuclei in the raw image. These are nuclear boundaries, not whole-cell boundaries.

Example pair: `01/t021.tif` and `01_GT/SEG/man_seg021.tif` (24 annotated objects).

## Verification performed
- ZIP CRC integrity check passed.
- All 184 raw TIFF images decoded successfully as 2D arrays.
- All 50 gold segmentation masks decoded as integer labels and matched the dimensions of their corresponding raw frames.
- SHA-256 recorded above for download reproducibility.

## Download again
Run from the repository root:

```bash
mkdir -p data/raw
curl --fail --location --retry 2 --output data/raw/Fluo-N2DH-GOWT1.zip https://data.celltrackingchallenge.net/training-datasets/Fluo-N2DH-GOWT1.zip
python -m zipfile -e data/raw/Fluo-N2DH-GOWT1.zip data/raw/Fluo-N2DH-GOWT1
```

## Attribution and use
Acknowledge the Cell Tracking Challenge and the data provider, Dr. E. Bártová, Institute of Biophysics, Academy of Sciences of the Czech Republic, Brno, Czech Republic. Follow the source conditions, including publication citation requirements. Public non-CTC scientific use and commercial use require the permissions specified by the source. Dataset redistribution/cloning is prohibited by the source; raw images and annotations remain local under the ignored `data/` directory. This repository provides source links rather than redistributing the dataset.
