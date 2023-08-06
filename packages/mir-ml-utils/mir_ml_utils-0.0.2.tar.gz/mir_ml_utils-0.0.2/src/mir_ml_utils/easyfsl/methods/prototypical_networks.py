"""
See original implementation (quite far from this one)
at https://github.com/jakesnell/prototypical-networks
"""

from typing import List
import torch
from torch import Tensor
import torch.nn as nn
from tqdm import tqdm

from src.easyfsl.methods.few_shot_classifier import FewShotClassifier
from src.easyfsl.utils import compute_prototypes
from src.loss_functions.loss_function_wrapper import LossFunctionWrapper


class PrototypicalNetworks(FewShotClassifier):
    """
    Jake Snell, Kevin Swersky, and Richard S. Zemel.
    "Prototypical networks for few-shot learning." (2017)
    https://arxiv.org/abs/1703.05175

    Prototypical networks extract feature vectors for both support and query images. Then it
    computes the mean of support features for each class (called prototypes), and predict
    classification scores for query images based on their euclidean distance to the prototypes.
    """

    def __init__(self, *args, **kwargs):
        """
        Raises:
            ValueError: if the backbone is not a feature extractor,
            i.e. if its output for a given image is not a 1-dim tensor.
        """
        super().__init__(*args, **kwargs)

        if len(self.backbone_output_shape) != 1:
            raise ValueError(
                "Illegal backbone for Prototypical Networks. "
                "Expected output for an image is a 1-dim tensor."
            )
        self.flatten_layer = nn.Flatten()

    def process_support_set(
        self,
        support_images: Tensor,
        support_labels: Tensor,
    ) -> None:
        """Overrides process_support_set of FewShotClassifier.
        Extract feature vectors from the support set and store class prototypes.

        Parameters
        ----------
        support_images: Images of the support set
        support_labels: Labels of the support set images

        Returns
        -------

        """

        support_features = self.backbone.forward(support_images)
        support_features = self.flatten_layer(support_features)
        #support_features = support_features.cpu()
        self.prototypes = compute_prototypes(support_features, support_labels)

        #if self.device == 'cuda:0':
        #    self.prototypes = self.prototypes.to(self.device)

    def forward(self, query_images: Tensor,) -> Tensor:
        """Overrides forward method of FewShotClassifier.
        Predict query labels based on their distance to class prototypes in the feature space.
        Classification scores are the negative of euclidean distances.

        Parameters
        ----------
        query_images: images of the query set

        Returns
        -------

         A prediction of classification scores for query images
        """

        if self.prototypes is None:
            raise ValueError("Prototypes not set up.")

        # Extract the features of support and query images
        z_query = self.backbone.forward(query_images)

        # flatten the result
        z_query = self.flatten_layer(z_query)

        # Compute the euclidean distance from queries to prototypes
        dists = torch.cdist(z_query, self.prototypes)

        # Use it to compute classification scores
        scores = -dists

        return self.softmax_if_specified(scores)

    @staticmethod
    def is_transductive() -> bool:
        return False


def epoch_fit_model(model: PrototypicalNetworks, optimizer: torch.optim.Optimizer,
                    criterion: LossFunctionWrapper,
                    data: torch.utils.data.DataLoader,
                    epoch_loss: List[float],
                    epoch_accuracy: List[float],
                    **kwargs):
    """ Do one epoch of model fit for the given prototypical network model

    Parameters
    ----------
    model: The model to fit
    optimizer: The optimizer
    criterion: The criteria to use for calculating the loss
    data
    epoch_loss
    epoch_accuracy
    kwargs

    Returns
    -------

    """

    if len(data) == 0:
        raise ValueError("Empty dataset given")

    with tqdm(enumerate(data), total=len(data), desc="Training") as tqdm_train:
        for episode_index, (support_images, support_labels, query_images, query_labels, _,) in tqdm_train:
            optimizer.zero_grad()

            if model.device == 'cuda:0' or model.device == 'cuda':
                # everything has to go to device if not already in there
                support_images = support_images.to(model.device)
                support_labels = support_labels.to(model.device)
                query_images = query_images.to(model.device)
                query_labels = query_labels.to(model.device)

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


def epoch_validation_fit_model(model: nn.Module,
                               criterion: LossFunctionWrapper,
                               data: torch.utils.data.DataLoader,
                               epoch_loss: List[float],
                               epoch_accuracy: List[float],
                               **kwargs):
    """

    Parameters
    ----------
    model
    criterion
    data
    epoch_loss
    epoch_accuracy
    kwargs

    Returns
    -------

    """

    if len(data) == 0:
        raise ValueError("Empty dataset given")

    epoch_prototypes: torch.Tensor = None
    n_itrs = 0
    with torch.no_grad():
        with tqdm(enumerate(data), total=len(data), desc="Validation") as tqdm_validate:
            for episode_index, (support_images, support_labels, query_images, query_labels, _,) in tqdm_validate:

                if model.device == 'cuda:0' or model.device == 'cuda':
                    # everything has to go to device if not already in there
                    support_images = support_images.to(model.device)
                    support_labels = support_labels.to(model.device)
                    query_images = query_images.to(model.device)
                    query_labels = query_labels.to(model.device)

                # create the prototypes for this batch
                model.process_support_set(support_images, support_labels)

                # get the model outputs
                outputs = model(query_images)
                loss = criterion(outputs, query_labels)

                epoch_loss.append(loss.loss.item())

                _, preds = torch.max(outputs, 1)
                n_preds = float(len(query_labels))
                ncorrect = torch.sum(preds == query_labels.data).item()

                # the epoch accuracy for this batch
                epoch_accuracy.append(ncorrect / n_preds)

                if episode_index == 0:
                    epoch_prototypes = model.prototypes
                else:
                    epoch_prototypes += model.prototypes

                n_itrs += 1

    # the epoch prototypes is the mean of all
    # the prototypes for the batches

    epoch_prototypes /= float(n_itrs)

    return epoch_prototypes
