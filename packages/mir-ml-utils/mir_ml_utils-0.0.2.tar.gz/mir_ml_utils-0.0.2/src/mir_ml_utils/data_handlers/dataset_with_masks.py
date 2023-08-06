"""

"""
from pathlib import Path
import numpy as np
from typing import List, Callable, Any
import torch
import torch.utils.data as data

from navalmartin_mir_vision_utils.image_loaders import (load_img, load_image_as_numpy, load_image_pytorch_tensor)
from mir_ml_utils.utils.mode_enum import ModeEnum
from mir_ml_utils.utils.exceptions import SizeMismatchException


class DatasetWithMasks(data.Dataset):

    @classmethod
    def from_file_sources(cls, imgs_filenames: List[Path],
                          masks_filenames: List[Path],
                          labels: List[int],
                          mode: ModeEnum = ModeEnum.TRAIN,
                          image_loader: Callable = load_img,
                          mask_loader: Callable = load_img,
                          on_load_transformers: Callable = None,
                          on_load_transformers_mask: Callable = None,
                          only_load_files: bool = False):
        """Build the image dataset from the given filenames and the specified
        labels

        Parameters
        ----------
        imgs_filenames: The filenames to load the dataset
        masks_filenames: The filenames for the masks
        labels: The labels of the images. This should be aligned with the filenames
        mode: The mode of the dataset
        image_loader: The callable that loads an image
        mask_loader: The callable that loads the masks
        on_load_transformers: The transformation to use when loading an image
        on_load_transformers_mask: Transformers for the mask images
        only_load_files: If True then only load the file name not the images
        Returns
        -------
        An instance of DatasetWithMasks
        """

        if len(labels) != 0 and len(imgs_filenames) != len(labels):
            raise SizeMismatchException(size1=len(imgs_filenames), size2=len(labels))

        # get the unique labels
        unique_labels = np.unique(labels)

        if only_load_files:

            # build an empty dataset
            dataset = DatasetWithMasks(mode=mode,
                                       unique_labels=list(unique_labels),
                                       only_load_files=only_load_files,
                                       transform=on_load_transformers,
                                       target_transform=None,
                                       mask_transform=on_load_transformers_mask)

            dataset.data = imgs_filenames
            dataset.masks = masks_filenames
        else:

            # build an empty dataset
            dataset = DatasetWithMasks(mode=mode,
                                       unique_labels=list(unique_labels),
                                       only_load_files=only_load_files,
                                       transform=None,
                                       target_transform=None,
                                       mask_transform=None)

            # actually load the images
            dataset.data = [image_loader(img_path, on_load_transformers) for img_path in imgs_filenames]
            dataset.masks = [mask_loader(mask_path, on_load_transformers_mask) for mask_path in masks_filenames]

        # populate the labels
        dataset.y = labels
        dataset.image_filenames = imgs_filenames
        return dataset

    def __init__(self, mode: ModeEnum, unique_labels: List[int],
                 transform: Callable = None,
                 target_transform: Callable = None,
                 mask_transform: Callable = None,
                 only_load_files: bool = False):
        super(DatasetWithMasks, self).__init__(mode=mode,
                                               unique_labels=unique_labels,
                                               transform=transform,
                                               target_transform=target_transform)

        self.mode = mode
        self.unique_labels: List[Any] = unique_labels
        self.transform: Callable = transform
        self.target_transform: Callable = target_transform
        self.y: List[int] = []
        self.data: List[Any] = []

        self.masks: List[np.array] = None
        self.image_filenames: List[str] = []
        self.mask_transform = mask_transform
        self.only_load_files = only_load_files

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

    def __getitem__(self, idx: int):

        if self.only_load_files:

            # load the file
            image_path = self.data[idx]
            mask_path = self.masks[idx]
            image = load_image_pytorch_tensor(path=image_path, transformer=self.transform)
            # note that we haven't converted the mask to RGB,
            # because each color corresponds to a different instance
            # with 0 being background
            mask = load_image_as_numpy(path=mask_path, transformer=self.mask_transform)

        else:

            # get image and label
            image, y = super(DatasetWithMasks, self).__getitem__(idx=idx)
            mask = self.masks[idx]

        # instances are encoded as different colors
        obj_ids = np.unique(mask)

        # first id is the background, so remove it
        obj_ids = obj_ids[1:]

        # split the color-encoded mask into a set
        # of binary masks
        masks = mask == obj_ids[:, None, None]

        # get bounding box coordinates for each mask
        num_objs = len(obj_ids)
        boxes = []
        for i in range(num_objs):
            pos = np.where(masks[i])
            xmin = np.min(pos[1])
            xmax = np.max(pos[1])
            ymin = np.min(pos[0])
            ymax = np.max(pos[0])
            boxes.append([xmin, ymin, xmax, ymax])

        boxes = torch.as_tensor(boxes, dtype=torch.float32)

        # there is only one class
        # TODO: Is this always true?
        labels = torch.ones((num_objs,), dtype=torch.int64)
        masks = torch.as_tensor(masks, dtype=torch.uint8)

        image_id = torch.tensor([idx])
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)

        target = {"boxes": boxes, "labels": labels,
                  "masks": masks, "image_id": image_id,
                  "area": area, "iscrowd": iscrowd}

        return image, target

    def __len__(self) -> int:
        """Returns the size of the datasets set

        Returns
        -------

        """
        if self.data is None:
            return 0
        return len(self.data)
