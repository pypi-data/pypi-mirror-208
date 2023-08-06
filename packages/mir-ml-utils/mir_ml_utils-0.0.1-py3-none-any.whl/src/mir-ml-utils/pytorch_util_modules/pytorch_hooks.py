"""module pytorch_hooks. Specifies various hooks we can
use around with PyTorch models.

check here:

"""

from typing import Any
import torch.nn as nn


class HookFwd(object):
    """forward hook class.
    check https://web.stanford.edu/~nanbhas/blog/forward-hooks-pytorch/
     on how to specify forward hooks for pytorch

    """
    def __init__(self, model: nn.Module):
        self.hook = model.register_forward_hook(self.hook_func)
        self.stored = None

    def __enter__(self, *args):
        return self

    def __exit__(self, *args):
        self.hook.remove()

    def hook_func(self, model: nn.Module, input: Any, output: Any):
        """

        Parameters
        ----------
        model
        input
        output

        Returns
        -------

        """
        self.stored = output.detach().clone()