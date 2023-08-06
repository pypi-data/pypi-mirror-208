from itertools import product

import numpy as np
import numpy.typing as npt


def cartesian_to_spherical(xyz: npt.ArrayLike):
    radial = np.sqrt(np.sum(xyz**2, axis=1))
    azimuthal = np.arctan2(xyz[:, 1], xyz[:, 0])
    polar = np.arccos(xyz[:, 2] / radial)
    return np.stack((polar, azimuthal, radial)).T


def normalize(arr):
    arr_s = arr - arr.min(axis=0)
    return arr_s / (arr_s.max(axis=0) + 1e-7)
