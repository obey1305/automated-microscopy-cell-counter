"""CSV reports and reference-aware prediction evaluation."""
import csv
import io
import numpy as np
from scripts.cell_analysis import count_cells


def export_cells_csv(filename, records, detected_count, retained_count):
    """Export all detections with filter decisions and repeated image-level counts."""
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=['image', 'detected_count', 'retained_count',
                                               'id', 'area_pixels', 'retained', 'exclusion_reason'])
    writer.writeheader()
    common = dict(image=filename, detected_count=detected_count, retained_count=retained_count)
    for record in records:
        writer.writerow(dict(**common, id=record['id'], area_pixels=record['area_pixels'],
                             retained=record['kept'], exclusion_reason=';'.join(record['reasons'])))
    if not records:
        writer.writerow(common)  # Preserve zero counts when no objects are detected.
    return stream.getvalue()


def evaluate_predictions(prediction, segmentation_gt, reference_count):
    """Count error versus tracking references; overlap on annotated GT instances only.

    Each GT object's best prediction IoU is averaged, including zeros for misses.
    This is not the official CTC SEG score or a whole-image accuracy metric.
    Unannotated foreground is not assumed to be background.
    """
    predicted = count_cells(prediction)
    count_cells(segmentation_gt)
    if prediction.shape != segmentation_gt.shape:
        raise ValueError('Prediction and reference shapes must match')
    if reference_count < 0:
        raise ValueError('Reference count cannot be negative')
    scores = []
    for label in np.unique(segmentation_gt[segmentation_gt > 0]):
        region = segmentation_gt == label
        ids, intersections = np.unique(prediction[region], return_counts=True)
        best = 0.0
        for candidate, intersection in zip(ids, intersections):
            if candidate == 0:
                continue
            union = int(region.sum()) + int(np.count_nonzero(prediction == candidate)) - int(intersection)
            best = max(best, float(intersection / union))
        scores.append(best)
    signed = predicted - reference_count
    return dict(predicted_count=predicted, reference_count=int(reference_count),
                signed_count_error=int(signed), absolute_count_error=int(abs(signed)),
                absolute_percentage_count_error=100 * abs(signed) / reference_count if reference_count else None,
                annotated_segmentation_objects=len(scores),
                mean_best_gt_iou=float(np.mean(scores)) if scores else None,
                gt_objects_iou_at_least_0_5=sum(score >= 0.5 for score in scores))
