import torch
from torchvision import transforms


def normalize_tensor(x: torch.Tensor) -> torch.Tensor:
    """

    Parameters
    ----------
    x

    Returns
    -------

    """

    # calculate mean and std
    mean, std = x.mean([1, 2]), x.std([1, 2])
    transform_norm = transforms.Compose([
        transforms.Normalize(mean, std)])
    return transform_norm(x)
