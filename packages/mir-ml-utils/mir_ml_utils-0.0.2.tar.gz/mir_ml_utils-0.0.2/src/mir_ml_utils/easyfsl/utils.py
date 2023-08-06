"""module easyfsl.utils
General utilities for few show learning.
This file is amended from https://github.com/sicara/easy-few-shot-learning

"""
import copy
from pathlib import Path
from typing import List, Tuple, TypeVar, Union

import torchvision
from matplotlib import pyplot as plt
import numpy as np
import torch
from torch import nn, Tensor
from tqdm import tqdm

LossFunctionWrapper = TypeVar('LossFunctionWrapper')
EasyFSLProtoNetClassifier = TypeVar('EasyFSLProtoNetClassifier')


def epoch_fit_model(model: nn.Module,
                    optimizer: torch.optim.Optimizer,
                    criterion: LossFunctionWrapper,
                    data: torch.utils.data.DataLoader,
                    epoch_loss: List[float],
                    epoch_accuracy: List[float],
                    device: str):
    """

    Parameters
    ----------

    model: The model to train
    optimizer: The optimizer to use
    criterion: The criterion or the loss function to use for training
    data: The training data
    epoch_loss: The list holding the epoch losses
    epoch_accuracy: The list holding the epoch accuracies
    device: The device type calculation is taking place

    Returns
    -------
    None
    """

    with tqdm(enumerate(data), total=len(data), desc="Training") as tqdm_train:
        for episode_index, (support_images, support_labels, query_images, query_labels, _,) in tqdm_train:
            optimizer.zero_grad()

            support_images = support_images.to(device)
            query_images = query_images.to(device)

            support_labels = support_labels.to(device)
            query_labels = query_labels.to(device)

            # compute prototypes
            model.process_support_set(support_images, support_labels)

            # compute predictions
            outputs = model(query_images)
            loss = criterion(outputs, query_labels)
            loss.loss.backward()
            optimizer.step()

            epoch_loss.append(loss.loss.item())

            _, preds = torch.max(outputs, 1)

            n_preds = float(len(query_labels))
            ncorrect = torch.sum(preds == query_labels.data).item()
            epoch_accuracy.append(ncorrect / n_preds)

            # if episode_index % app_config.config.LOG_UPDATE_FREQUENCY == 0:
            #    tqdm_train.set_postfix(loss=sliding_average(train_loss, app_config.config.LOG_UPDATE_FREQUENCY ))


def epoch_validation_fit_model(model: Union[nn.Module | EasyFSLProtoNetClassifier],
                               criterion: LossFunctionWrapper,
                               data: torch.utils.data.DataLoader,
                               epoch_loss: List[float],
                               epoch_accuracy: List[float],
                               device: str, **kwargs) -> None:
    """Helper function to use when validating few-shot learning models
    with PyTorchTrainer

    Parameters
    ----------
    model: The model to validate
    criterion: The criterion or the loss function to use for validation
    data: The validation data
    epoch_loss: The list holding the epoch losses
    epoch_accuracy: The list holding the epoch accuracies
    Returns
    -------
    None
    """

    with torch.no_grad():
        with tqdm(enumerate(data), total=len(data), desc="Validation") as tqdm_train:

            best_accuracy = kwargs['best_accuracy'] if 'best_accuracy' in kwargs else float("-inf")
            for episode_index, (support_images, support_labels, query_images, query_labels, _,) in tqdm_train:

                support_images = support_images.to(device)
                query_images = query_images.to(device)
                support_labels = support_labels.to(device)
                query_labels = query_labels.to(device)

                model.process_support_set(support_images, support_labels)
                outputs = model(query_images)
                loss = criterion(outputs, query_labels)

                epoch_loss.append(loss.loss.item())

                _, preds = torch.max(outputs, 1)
                n_preds = float(len(query_labels))
                ncorrect = torch.sum(preds == query_labels.data).item()

                computed_accuracy = ncorrect / n_preds
                epoch_accuracy.append(ncorrect / n_preds)

                if 'save_model_prototypes_on_validation' in kwargs:
                    if computed_accuracy >= best_accuracy:
                        model.save_prototypes(filename=kwargs['best_accuracy_prototypes_filepath'])
                        best_accuracy = computed_accuracy


def compute_backbone_output_shape(backbone: nn.Module) -> Tuple[int]:
    """
    Compute the dimension of the feature space defined by a feature extractor.
    Args:
        backbone: feature extractor

    Returns:
        shape of the feature vector computed by the feature extractor for an instance

    """
    input_images = torch.ones((4, 3, 32, 32))
    # Use a copy of the backbone on CPU, to avoid device conflict
    output = copy.deepcopy(backbone).cpu()(input_images)

    return tuple(output.shape[1:])


def compute_prototypes(support_features: Tensor,
                       support_labels: Tensor) -> Tensor:
    """ Compute class prototypes from support features and labels

    Parameters
    ----------
    support_features: for each instance in the support set, its feature vector
    support_labels: for each instance in the support set, its label

    Returns
    -------

    For each label of the support set, the average feature vector of instances with this label
    """

    n_way = len(torch.unique(support_labels))
    # Prototype i is the mean of all
    # instances of features corresponding to labels == i
    return torch.cat(
        [
            support_features[torch.nonzero(support_labels == label)].mean(0)
            for label in range(n_way)
        ]
    )


def entropy(logits: Tensor) -> Tensor:
    """Compute entropy of prediction.
    Notice that the input is assumed to be logit and not probability.

    Parameters
    ----------
    logits: shape (n_images, n_way)

    Returns
    -------

    Tensor: shape(), Mean entropy.
    """

    probabilities = logits.softmax(dim=1)
    return (-(probabilities * (probabilities + 1e-12).log()).sum(dim=1)).mean()
