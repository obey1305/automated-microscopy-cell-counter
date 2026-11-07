"""Streamlit microscopy upload and numbered segmentation interface."""
from pathlib import Path
import os
ROOT = Path(__file__).resolve().parent
os.environ['CELLPOSE_LOCAL_MODELS_PATH'] = str(ROOT / '.cellpose/models')

import hashlib
import numpy as np
import streamlit as st
import torch
from cellpose import models
from scripts.cell_analysis import count_cells, filter_cells
from scripts.image_tools import load_image, display_rgb, numbered_overlay

st.set_page_config(page_title='Microscopy Cell Counter', layout='wide')
st.title('Microscopy Cell Counter')
st.write('Upload a microscope image, run Cellpose, and inspect numbered cell outlines.')
st.caption('Predictions need visual review. Nuclear images produce nuclear areas rather than whole-cell areas.')


@st.cache_resource
def get_model():
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    return models.CellposeModel(pretrained_model='cpsam_v2', device=device, use_bfloat16=False)


upload = st.file_uploader('Upload a microscopy image', type=['png', 'jpg', 'jpeg', 'tif', 'tiff'],
                          help='Single 2D grayscale or RGB image, up to 4096 × 4096 pixels.')
sample = ROOT / 'data/raw/Fluo-N2DH-GOWT1/Fluo-N2DH-GOWT1/01/t021.tif'
if sample.is_file():
    use_sample = st.checkbox('Use the local sample image', value=False)
else:
    use_sample = False

if upload is not None:
    data, filename = upload.getvalue(), upload.name
elif use_sample:
    data, filename = sample.read_bytes(), 't021.tif'
else:
    st.info('Choose an image above to begin.')
    st.stop()

try:
    image = load_image(data, filename)
except Exception as exc:
    st.error(f'Unable to read this image: {exc}')
    st.stop()

key = hashlib.sha256(data).hexdigest()
if st.session_state.get('image_key') != key:
    st.session_state['image_key'] = key
    st.session_state.pop('masks', None)
st.subheader(filename)
st.caption(f'{image.shape[1]} × {image.shape[0]} pixels · {image.dtype}')

with st.sidebar:
    st.header('Object filters')
    min_area = st.number_input('Minimum area (pixels)', min_value=0, value=0, step=100)
    limit_max = st.checkbox('Limit maximum area')
    max_area = st.number_input('Maximum area (pixels)', min_value=0, value=10000, step=100) if limit_max else None
    exclude_border = st.checkbox('Exclude objects touching borders')
    st.caption('Filters can exclude real cells. IDs remain stable when filters change.')

left, right = st.columns(2)
left.image(display_rgb(image), caption='Original image', width='stretch')
if st.button('Detect cells', type='primary'):
    try:
        with st.spinner('Running Cellpose. First use downloads model weights and may take several minutes.'):
            masks, _, _ = get_model().eval(image, channel_axis=-1 if image.ndim == 3 else None,
                                          batch_size=1, normalize=True, min_size=15)
            st.session_state['masks'] = np.asarray(masks)
    except Exception as exc:
        st.error(f'Cellpose could not analyze this image: {exc}')

if 'masks' in st.session_state:
    masks = st.session_state['masks']
    if max_area is not None and max_area < min_area:
        st.error('Maximum area must be at least the minimum area.')
        st.stop()
    filtered, records = filter_cells(masks, int(min_area), int(max_area) if max_area is not None else None, exclude_border)
    overlay, _ = numbered_overlay(image, filtered)
    right.image(overlay, caption='Orange outlines · Cyan identification numbers', width='stretch')
    a, b, c = st.columns(3)
    a.metric('Detected objects', count_cells(masks))
    b.metric('Retained objects', count_cells(filtered))
    c.metric('Excluded objects', count_cells(masks) - count_cells(filtered))
    if count_cells(filtered) == 0:
        st.info('No objects remain. Review the image and filter settings.')
    st.dataframe([dict(ID=r['id'], Area_pixels=r['area_pixels'], Retained=r['kept'],
                       Exclusion_reason=', '.join(r['reasons'])) for r in records], hide_index=True)
else:
    right.info('Select Detect cells to display numbered outlines.')
