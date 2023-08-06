"""module distance_functions. Provides various
distance metrics

"""

import torch

from src.loss_functions.distance_type import DistanceType
from src.utils.exceptions import SizeMismatchException


def load_distance_functions() -> dict:
    """Loads the distance metric functions available

    Returns
    -------

    A dictionary of the distance metrics
    """
    distance_metric_map = {DistanceType.L2_DISTANCE: l2_dist}
    return distance_metric_map


def l2_dist(x: torch.Tensor, y: torch.Tensor) -> float:
    """Computes the euclidean distance between two tensors.
    The implementation is more tailored towards prototypical loss
    calculations

    Parameters
    ----------
    x
    y

    Returns
    -------

    """

    # x: N x D
    # y: M x D
    n = x.size(0)
    m = y.size(0)
    d = x.size(1)

    if d != y.size(1):
        raise SizeMismatchException(size1=d, size2=y.size(1))

    x = x.unsqueeze(1).expand(n, m, d)
    y = y.unsqueeze(0).expand(n, m, d)

    return torch.pow(x - y, 2).sum(2)
