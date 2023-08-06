from ..text_block import Line
from ..segment import Segment
from .constants import (
    MIN_NUMBER_OF_LINES_FOR_TWO_COLUMNS,
    TWO_COLUMNS_SEPARATOR_MIN_THRESHOLD,
    TWO_COLUMNS_SEPARATOR_MAX_THRESHOLD,
    COLUMN_MIN_WIDTH,
    MAX_SCORE_THRESHOLD,
)
from sklearn.cluster import KMeans
import numpy as np


def k_means_fixed_centroids_score_per_line(
    line: Line, first_centroid: float, second_centroid: float
) -> float:
    """
    Get the distance of the center of line from the closest centroid on the horizontal axis"""
    x_center = line.bounding_box.get_center().x
    left_distance = abs(x_center - first_centroid)
    right_distance = abs(x_center - second_centroid)
    return min(left_distance, right_distance)


def k_means_fixed_centroids_score(
    lines: list[Line], first_centroid: float, second_centroid: float
) -> float:
    """
    Averaging the k means score of each line. Look at the function k_means_score_per_line for more details.
    """
    if not lines:
        return 1
    scores = [
        k_means_fixed_centroids_score_per_line(line, first_centroid, second_centroid)
        for line in lines
    ]
    average_score = sum(scores) / len(lines)
    return average_score


#! Not in use!
def k_means_score(lines: list[Line]) -> float:
    """
    Notice the inertia score is taken the square of the distance i.e. l2 norm
    and not l1 like we use the code
    """
    if len(lines) < 2:
        return 1
    x_centers = [line.bounding_box.get_center().x for line in lines]
    x_centers = np.array(x_centers).reshape(-1, 1)
    kmeans = KMeans(n_clusters=2)
    kmeans.fit(x_centers)
    score = kmeans.inertia_
    average_score = score / len(lines)
    return average_score


def is_two_columns(lines: list[Line]):
    """
    Get the segments of the lines
    """
    if len(lines) < MIN_NUMBER_OF_LINES_FOR_TWO_COLUMNS:
        return False
    horizontal_segments = [line.bounding_box.get_horizontal_segment() for line in lines]
    segment_clusters = Segment.merge_segments(horizontal_segments)
    if len(segment_clusters) != 2:
        return False
    first_segment, second_segment = segment_clusters
    if (
        first_segment.get_length() < COLUMN_MIN_WIDTH
        or second_segment.get_length() < COLUMN_MIN_WIDTH
    ):
        return False
    if (
        first_segment.get_right() < TWO_COLUMNS_SEPARATOR_MIN_THRESHOLD
        or first_segment.get_left() > TWO_COLUMNS_SEPARATOR_MAX_THRESHOLD
    ):
        return False
    first_centroid = first_segment.get_center()
    second_centroid = second_segment.get_center()
    score = k_means_fixed_centroids_score(lines, first_centroid, second_centroid)
    return score < MAX_SCORE_THRESHOLD
