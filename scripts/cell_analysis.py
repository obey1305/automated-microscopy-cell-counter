"""Analysis helpers for 2D instance-label segmentation masks."""
import numpy as np


def count_cells(masks: np.ndarray) -> int:
    """Count distinct positive instance IDs; zero is background.

    Counts predicted objects, including objects touching image borders.
    IDs need not be consecutive. A binary foreground mask counts as one
    instance; use an instance segmentation mask to count individual cells.
    """
    masks = np.asarray(masks)
    if masks.ndim != 2 or not np.issubdtype(masks.dtype, np.integer):
        raise ValueError('Expected a 2D integer instance-label mask')
    if np.any(masks < 0):
        raise ValueError('Instance labels must be nonnegative')
    return int(np.unique(masks[masks > 0]).size)


def measure_cell_areas(masks: np.ndarray) -> list[dict]:
    """Return each original instance ID and its area in pixels (not microns)."""
    count_cells(masks)  # Validate the instance-label mask.
    ids, areas = np.unique(np.asarray(masks), return_counts=True)
    return [{'id': int(i), 'area_pixels': int(a)} for i, a in zip(ids, areas) if i > 0]


def filter_cells(masks: np.ndarray, min_area: int = 1000,
                 max_area: int | None = None, exclude_border: bool = False):
    """Return a new filtered mask and an audit record for every original ID.

    Area bounds are inclusive. Border exclusion can remove real partial cells.
    Rules flag candidate artifacts; they do not establish segmentation accuracy.
    Retained IDs are preserved and rejected objects become background zero.
    """
    for value in (min_area, max_area):
        if value is not None and (isinstance(value, (bool, np.bool_)) or
                                 not isinstance(value, (int, np.integer)) or value < 0):
            raise ValueError('Area limits must be nonnegative integers')
    if max_area is not None and max_area < min_area:
        raise ValueError('max_area must be at least min_area')
    records = measure_cell_areas(masks)
    masks = np.asarray(masks)
    filtered = masks.copy()
    border_ids = set()
    if masks.size:
        border_ids = set(np.unique(np.concatenate((masks[0], masks[-1], masks[:, 0], masks[:, -1]))))
    for record in records:
        reasons = []
        if record['area_pixels'] < min_area:
            reasons.append('too_small')
        if max_area is not None and record['area_pixels'] > max_area:
            reasons.append('too_large')
        touches_border = record['id'] in border_ids
        if exclude_border and touches_border:
            reasons.append('touches_border')
        record.update(touches_border=touches_border, kept=not reasons, reasons=reasons)
        if reasons:
            filtered[masks == record['id']] = 0
    return filtered, records
