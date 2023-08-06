"""
Some useful functions for ST-polynomial decomposition.

By Edo van Veen @ Nynke Dekker Lab, TU Delft (2021)
"""
import numpy as np
from scipy.spatial.distance import cdist


def find_neighbours(locs0, locs1, threshold):
    """For each coordinate in locs0 (shape (N, 2)), find the nearest coordinate in locs1 (shape (M, 2)),
    within some threshold distance. Returns a np.array, with mapping_0to1[i] = j connecting a spot index i from
    locs0 to a spot index j from locs1. If no neighbor is found, j == -1."""
    dists = cdist(locs0, locs1)
    mapping_0to1 = np.zeros(len(locs0), dtype=int)
    for i in range(len(locs0)):
        if np.amin(dists[i, :]) < threshold:
            mapping_0to1[i] = np.argmin(dists[i, :])
        else:
            mapping_0to1[i] = -1
    return mapping_0to1


def make_pairs(locs0, locs1, mapping_0to1):
    """Using the mapping_0to1 map from find_neighbours(), make two ordered lists of spots. At each index i,
    locs0_pairs[i] and locs1_pairs[i] are neighbours."""
    # Make final list of locs
    locs0_pairs = []
    locs1_pairs = []
    for i in range(len(mapping_0to1)):
        j = mapping_0to1[i]
        if j >= 0:
            locs0_pairs.append(locs0[i, :])
            locs1_pairs.append(locs1[j, :])
    locs0_pairs = np.array(locs0_pairs)
    locs1_pairs = np.array(locs1_pairs)
    return locs0_pairs, locs1_pairs


def loc_to_unitcircle(locs_abs, fig_size, center=None, rescale=1):
    """Rescale locs_abs (shape (N, 2)) from pixel coordinates to unit circle coordinates, using the figure size fig_size
    (list of 2 ints). Optionally, a pixel location can be chosen manually to become the unit circle center,
    and an additional rescale factor can be given."""

    # Prepare.
    if center is None:
        center = np.array([fig_size[0] / 2, fig_size[1] / 2])
    dist_x = np.amax([center[0], fig_size[0] - center[0]])
    dist_y = np.amax([center[1], fig_size[1] - center[1]])
    scale_factor = 1 / np.linalg.norm([dist_x, dist_y])
    extra_scale_factor = rescale  # np.clip(rescale, 0, 1)

    # Rescale.
    locs = locs_abs - np.array(center).reshape((1, 2))
    locs = scale_factor * extra_scale_factor * locs
    return locs, 1 / (scale_factor * extra_scale_factor)


def unitcircle_to_loc(locs, fig_size, center=None, rescale=1):
    """Rescale locs (shape (N, 2)) from unit circle coordinates to pixel coordinates, using the figure size fig_size
    (list of 2 ints). Optionally, a pixel location can be chosen manually for the unit circle center to transform to,
    and an additional rescale factor can be given."""

    # Prepare.
    if center is None:
        center = np.array([fig_size[0] / 2, fig_size[1] / 2])
    dist_x = np.amax([center[0], fig_size[0] - center[0]])
    dist_y = np.amax([center[1], fig_size[1] - center[1]])
    scale_factor = 1 / np.linalg.norm([dist_x, dist_y])
    extra_scale_factor = rescale  # np.clip(rescale, 0, 1)

    locs = locs / (scale_factor * extra_scale_factor)
    locs_abs = locs + np.array(center).reshape((1, 2))

    return locs_abs
