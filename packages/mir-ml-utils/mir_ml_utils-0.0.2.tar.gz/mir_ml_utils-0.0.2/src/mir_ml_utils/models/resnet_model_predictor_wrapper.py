from typing import Callable
import torch
from torchcam.methods import GradCAM
from mir_ml_utils.utils.exceptions import SizeMismatchException


class ResNetPredictorWrapper(object):
    def __init__(self, model: torch.nn.Module, transform_prediction: Callable):
        self.model: torch.nn.Module = model
        self.transform_prediction: Callable = transform_prediction

    def predict(self, input: torch.Tensor) -> torch.Tensor:

        # expect only one tensor
        if len(input) != 1:
            raise SizeMismatchException(size1=len(input), size2=1)

        output = self.model(input)

        if self.transform_prediction is not None:
            output = self.transform_prediction(output)

        return output

    def get_activation_map(self, input: torch.Tensor, input_dim: int = 3):
        """Returns the activation map for the given input

        Parameters
        ----------
        input: The image as a torch.Tensor
        input_dim: The expected dimension of the input. Either 3 or 1
        Returns
        -------

        """

        # expect only one tensor
        if len(input) != input_dim:
            raise SizeMismatchException(size1=len(input), size2=1)

        # the extractor for the class activation
        cam_extractor = GradCAM(self.model, target_layer=self.model.layer4)

        # forward pass the input
        out = self.model(torch.stack([input]))

        # get the activation map for the input
        activation_map = cam_extractor(out.argmax().item(), out)
        return activation_map