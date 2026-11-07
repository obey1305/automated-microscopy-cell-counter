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
