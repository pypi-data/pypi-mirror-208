from pathlib import Path

from typing import List, Callable, Any
import numpy as np
import torch
import torch.utils.data as data

from navalmartin_mir_vision_utils.mir_vision_io import LabeledImageDataset
from navalmartin_mir_vision_utils.image_loaders import load_img
from mir_ml_utils.utils.mode_enum import ModeEnum
from mir_ml_utils.utils.exceptions import SizeMismatchException


class ImagesDataset(data.Dataset):
    """Simple class to load image datasets.

    """

    @classmethod
    def from_file_sources(cls, filenames: List[Path], labels: List[int],
                          mode: ModeEnum = ModeEnum.TRAIN,
                          image_loader: Callable = load_img,
                          on_load_transformers: Callable = None) -> "ImagesDataset":
        """Build the image dataset from the given filenames and the specified
        labels

        Parameters
        ----------
        filenames: The files names to load the dataset
        labels: The labels of the images. This should be aligned with the filenames
        mode: The mode of the dataset
        image_loader: The callable that laods an image
        on_load_transformers: The transformation to use when loading an image

        Returns
        -------
        An instance of ImagesDataset
        """

        if len(filenames) != len(labels):
            raise SizeMismatchException(size1=len(filenames), size2=len(labels))

        # get the unique labels
        unique_labels = np.unique(labels)

        # build an empty dataset
        dataset = ImagesDataset(mode=mode, unique_labels=list(unique_labels))

        # populate the labels
        dataset.y = labels

        # actually load the images
        dataset.data = [image_loader(img_path, on_load_transformers) for img_path in filenames]

        return dataset

    @classmethod
    def from_images_and_labels(cls, x: torch.Tensor, y: torch.Tensor,
                               mode: ModeEnum = ModeEnum.TRAIN) -> "ImagesDataset":
        """Load the dataset from the given Tensor of image data
        and the labels corresponding to the images

        Parameters
        ----------
        x: The Tensor that holds the images data
        y: The Tensor that holds the labels
        mode: The mode of the dataset

        Returns
        -------

        An instance of ImagesDataset
        """

        unique_labels = np.unique(y)

        # build an empty dataset
        dataset = ImagesDataset(mode=mode, unique_labels=list(unique_labels),
                                transform=None, target_transform=None)

        # populate the labels
        dataset.y = y

        # actually load the images
        dataset.data = x

        return dataset

    @classmethod
    def from_labeled_image_dataset(cls, labeled_images: LabeledImageDataset,
                                   mode: ModeEnum = ModeEnum.TRAIN,
                                   transformer: Callable = None) -> "ImagesDataset":
        """Load the images from the given LabeledImageDataset

        Parameters
        ----------
        transformer
        mode
        cls
        labeled_images

        Returns
        -------
        An instance of ImagesDataset
        """

        tensor_images, labels = LabeledImageDataset.as_pytorch_tensor(labeled_images, transformer)

        unique_labels: List[int] = []
        if isinstance(labeled_images.unique_labels[0], tuple):
            for label in labeled_images.unique_labels:
                unique_labels.append(label[1])
        elif isinstance(labeled_images.unique_labels[0], int):
            unique_labels = labeled_images.unique_labels
        else:
            raise ValueError("Invalid label type. Label should be either a tuple or an int")

        # build an empty dataset
        dataset = ImagesDataset(mode=mode,
                                unique_labels=unique_labels,
                                transform=None,
                                target_transform=None)

        # populate the labels
        dataset.y = labels

        # load the images
        dataset.data = tensor_images

        return dataset

    def __init__(self, mode: ModeEnum, unique_labels: List[int],
                 transform: Callable = None, target_transform: Callable = None):
        """

        Parameters
        ----------
        mode: The mode of the dataset
        transform: Transformation for the input
        target_transform: Transformation for the target
        """

        super(ImagesDataset, self).__init__()
        self.mode = mode
        self.unique_labels: List[Any] = unique_labels
        self.transform: Callable = transform
        self.target_transform: Callable = target_transform
        self.y: List[int] = []
        self.data: List[Any] = []

    @property
    def n_classes(self) -> int:
        return len(self.unique_labels)

    @property
    def labels(self) -> List[int]:
        """ Returns the labels list

        Returns
        -------
        """
        return self.y

    def get_labels(self) -> List[int]:
        """Extra function to return the labels of the dataset.
        This is needed in order to respect the interface of the
        FewShotDataset

        Returns
        -------

        """
        return self.labels

    @property
    def images(self) -> torch.Tensor:
        return self.data

    def __getitem__(self, idx: int) -> tuple:
        """Returns the idx-th datasets point
        in the datasets set. All PyTorch datasets, including
        few-shot datasets, need a __getitem__ method.

        Parameters
        ----------
        idx: The index of the data to request

        Returns
        -------
        """

        x = self.data[idx]
        if self.transform:
            x = self.transform(x)

        y = self.y[idx]
        if self.target_transform:
            y = self.target_transform(y)

        return x, y

    def __len__(self):
        """Returns the size of the datasets set.
        All PyTorch datasets, including few-shot datasets, need a __len__ method.

        Returns
        -------

        """
        if self.data is None:
            return 0
        return len(self.data)

