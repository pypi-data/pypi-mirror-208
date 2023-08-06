from typing import List
import torch.nn as nn

from src.pytorch_util_modules.flatten_module import Flatten


def conv_2d_block(in_channels, out_channels, kernel_size, padding):
    """Build a convolutional block

    Parameters
    ----------
    in_channels
    out_channels
    kernel_size
    padding

    Returns
    -------

    """
    return nn.Sequential(
        nn.Conv2d(in_channels, out_channels, kernel_size, padding=padding),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(),
        nn.MaxPool2d(2)
    )


def build_conv_2d_encoder(num_conv_blocks: int,
                          img_dim: List[int],
                          hidden_layer_dim: int,
                          z_space_dim: int,
                          kernel_size: int = 3, padding: int = 1) -> nn.Sequential:

    """Builds the default encoder for the prototypical network

    Parameters
    ----------
    img_dim: The dimension of the input image
    hid_dim: The dimension of the hidden layers
    z_dim: The z-space dimension
    kernel_size
    padding

    Returns
    -------

    An instance of nn.Sequential
    """

    encoder = nn.Sequential(conv_2d_block(img_dim[0], hidden_layer_dim, kernel_size=kernel_size, padding=padding))

    for block in range(num_conv_blocks - 2):
        encoder.append(conv_2d_block(hidden_layer_dim, hidden_layer_dim, kernel_size=kernel_size, padding=padding))

    encoder.append(conv_2d_block(hidden_layer_dim, z_space_dim, kernel_size=kernel_size, padding=padding))
    encoder.append(Flatten())
    return encoder
