"""module img_transformers. Various utilities
for transforming images

"""
import enum
from typing import Callable, List
import numpy as np
from PIL import Image
from PIL import ImageOps
import torchvision.transforms as transforms

import torch


class ImageAugmentType(enum.Enum):
    INVALID = 0
    RANDOM_CROP = 1
    COLOR_JITTER = 2


class ImageTransformerWrapper(object):
    def __init__(self, transform_op: Callable, *args):
        self.transform_op = transform_op
        self.args = args

    def __call__(self, img: Image):
        if self.args is not None and len(self.args) != 0 and self.args[0] is not None:
            return self.transform_op(img, *self.args)
        else:
            return self.transform_op(img)


def to_pytorch_tensor(img: Image, unsqueeze_dim: int = 0) -> torch.Tensor:
    """Converts the PIL.Image item into a torch.Tensor

    Parameters
    ----------
    img: The PIL.Image to convert
    unsqueeze_dim: The dimension to unsqueeze the produced torch tensor

    Returns
    -------

    An instance of torch.Tensor
    """

    if unsqueeze_dim is None or unsqueeze_dim == -1:
        return transforms.ToTensor()(img)
    else:
        return transforms.ToTensor()(img).unsqueeze_(unsqueeze_dim)


def pytorch_tensor_to_numpy(img: torch.Tensor):
    return img.cpu().detach().numpy()


def pil_image_from_array(img: List):
    return Image.fromarray(np.uint8(img))


def resize_image(img: Image, size: tuple) -> Image:
    """Resize the image on the given size

    Parameters
    ----------
    img: The image to resize
    size: The size to resize the image

    Returns
    -------

    """
    img = img.resize(size)
    return img


def to_grayscale(img: Image) -> Image:
    """Converts the given image to greyscale

    Parameters
    ----------
    img: The image to convert to grayscale

    Returns
    -------

    A grey-scaled image
    """
    # makes it greyscale
    return ImageOps.grayscale(img)


def to_rgb(image: Image) -> Image:
    """Convert the PIL.Image to RGB. This function
    can be used to convert a PNG image to JPG/JPEG
    formats. Note that this function simply returns the
    converted image. It does not save the newly formatted image

    Parameters
    ----------
    image: The Image to convert

    Returns
    -------

    An Instance of PIL.Image
    """

    # don't convert anything if the
    # image is in the right mode
    if image.mode == 'RGB':
        return image

    return image.convert("RGB")
