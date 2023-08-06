"""module prototypical_loss. Provides implementation
of the calculation of the loss function for PrototypicalNet model
The original implementation comes from: https://github.com/orobix/Prototypical-Networks-for-Few-shot-Learning-PyTorch
"""

from dataclasses import dataclass
from pathlib import Path
import torch
from torch.nn import functional as F

from src.loss_functions.distance_type import DistanceType
from src.loss_functions import DISTANCE_METRIC_MAP
from src.loss_functions.loss_function_result import LossFuncResult


@dataclass(init=True, repr=True)
class PrototypicalLossFuncResult(LossFuncResult):
    """Specialization of LossFuncResult for
    prototypical loss. Allows to save the
    computed prototypes

    """
    prototypes: torch.Tensor = None

    def save(self, filename: Path) -> None:
        torch.save(self.prototypes, filename)


@dataclass(init=True, repr=True)
class PrototypicalLossConfig:
    distance_type: DistanceType = None
    log_softmax_dim: int = 0

    # number of points in S_k i.e. number of support points
    # per class for computing the prototypes. Assume
    # that for every class this will be the same number
    n_support_pts_per_cls: int = 0


class PrototypicalLoss(object):
    """Wrapper class that implements the prototypical loss
    for PrototypicalNet

    """
    def __init__(self, config: PrototypicalLossConfig):

        if config.distance_type is None:
            raise ValueError("distance type is None")

        # raise if invalid distance type
        if config.distance_type == DistanceType.INVALID:
            raise ValueError("distance type is INVALID")

        self.config = config

    def __call__(self, input: torch.Tensor, target: torch.Tensor) -> PrototypicalLossFuncResult:
        return self.loss(input=input, target=target)

    def loss(self, input: torch.Tensor, target: torch.Tensor) -> PrototypicalLossFuncResult:
        """Compute the barycentres by averaging the features of n_support
        samples for each class in target, computes then the distances from each
        samples' features to each one of the barycentres, computes the
        log_probability for each n_query samples for each one of the current
        classes, of appartaining to a class c, loss and accuracy are then computed
        and returned

        Parameters
        ----------
        input: The model output for a batch of samples
        target: Ground truth for the above batch of samples.
        This will be the query set when training

        Returns
        -------

        """

        if self.config.n_support_pts_per_cls <= 0:
            raise ValueError(f"Invalid number of support points per class {self.config.n_support_pts_per_cls}. "
                             f"Should be greater than zero.")

        # get a copy of the tensors from the GPU
        target_cpu = target.to('cpu')
        input_cpu = input.to('cpu')

        if self.config.n_support_pts_per_cls >= len(target_cpu):
            raise ValueError("Invalid number of support points. "
                             "n_support_pts_per_cls should be < len(target_cpu)")

        def supp_idxs(c):
            # FIXME when torch will support where as np
            return target_cpu.eq(c).nonzero()[:self.config.n_support_pts_per_cls].squeeze(1)

        # FIXME when torch.unique will be available on cuda too
        classes = torch.unique(target_cpu)
        n_classes = len(classes)

        # FIXME when torch will support where as np
        # assuming n_query, n_target constants
        # the number of query pts...This may give
        # zero n_query points though!!!
        n_query = target_cpu.eq(classes[0].item()).sum().item() - self.config.n_support_pts_per_cls
        #n_query = len(target_cpu) - self.config.n_support_pts_per_cls

        if n_query <= 0:
            raise ValueError(f"Invalid number of query points={n_query}. "
                             f"Should be greater than zero.")

        # get the support indexes to form the prototypes
        support_idxs = list(map(supp_idxs, classes))

        # create the prototypes
        prototypes = torch.stack([input_cpu[idx_list].mean(0) for idx_list in support_idxs])

        # TODO: We should have as many prototypes as n_classes
        # TODO: what happens if prototypes contain nan?
        if len(prototypes) != n_classes:
            raise ValueError(f"Invalid number of prototypes {len(prototypes)} != {n_classes}")

        # check for nans
        if torch.sum(torch.isnan(prototypes), dtype=torch.uint8) != 0:
            raise ValueError("Prototypes are  nan")

        # FIXME when torch will support where as np
        query_idxs = torch.stack(list(map(lambda c: target_cpu.eq(c).nonzero()[self.config.n_support_pts_per_cls:],
                                          classes))).view(-1)

        query_samples = input.to('cpu')[query_idxs]
        dists = DISTANCE_METRIC_MAP[self.config.distance_type](query_samples, prototypes)

        # While mathematically equivalent to log(softmax(x)), doing
        # these two operations separately is slower and numerically unstable.
        # This function uses an alternative formulation to compute
        # the output and gradient correctly.
        log_p_y = F.log_softmax(-dists, dim=self.config.log_softmax_dim).view(n_classes, n_query, -1)

        target_inds = torch.arange(0, n_classes)
        target_inds = target_inds.view(n_classes, 1, 1)
        target_inds = target_inds.expand(n_classes, n_query, 1).long()

        loss_val = -log_p_y.gather(2, target_inds).squeeze().view(-1).mean()
        _, y_hat = log_p_y.max(2)
        acc_val = y_hat.eq(target_inds.squeeze(2)).float().mean()

        return PrototypicalLossFuncResult(loss=loss_val,
                                          accuracy=acc_val,
                                          prototypes=prototypes)
