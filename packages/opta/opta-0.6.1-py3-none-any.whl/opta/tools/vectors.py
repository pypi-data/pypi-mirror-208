import numpy as np


def bound_vector(x, bounds):
    """Pushes input vector `x` to the area described via `bounds`"""
    return np.clip(x, a_min=bounds[:, 0], a_max=bounds[:, 1])


def generate_vector_in_area(area):
    """Generates vector inside the given rectangular `area`"""
    left, right = area[:, 0], area[:, 1]
    vector = left + np.random.rand(area.shape[0]) * (right - left)
    return vector


def generate_vector_in_sphere(current_point, radius):
    """Generates vector inside the given sphere with the center in `current_point` with `radius`"""
    normally_distributed = np.random.normal(0.0, 1.0, len(current_point))
    normally_distributed /= np.linalg.norm(normally_distributed)
    shift = np.random.uniform(0.0, radius) * normally_distributed
    moved_vector = current_point + shift
    return moved_vector
