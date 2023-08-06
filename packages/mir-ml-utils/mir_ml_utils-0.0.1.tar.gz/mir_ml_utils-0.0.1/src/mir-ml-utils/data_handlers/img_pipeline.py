"""module img_pipeline. Defines a simple wrapper
of transformations applied on images. Each transformation
should expose the __call__(img) function.
A transformation may be a series of transformations
like PyTorch.transform.

"""
from typing import Callable, List
from PIL import Image


class ImgPipelineItem(object):
    """Utility wrapper for image
    operations that take arguments. The arguments
    are passed as arguments upon constructing the
    pipeline item and should be in the same order as
    needed by the applied callable

    """
    def __init__(self, op: Callable, *args):
        """Initialize the pipeline item

        Parameters
        ----------
        op: The operation to apply on the image
        args: The arguments for the operation
        """
        self.op = op
        self.args = args

    def __call__(self, image: Image) -> Image:
        """Apply the pipeline item on the given image

        Parameters
        ----------
        image: The  image to use

        Returns
        -------

        """
        return self.op(image, *self.args)


class ImgPipeline(object):
    """The class ImgPipeline.Defines a simple wrapper
    of transformations applied on images. Each transformation
    should expose the __call__(img) function.
    A transformation may be a series of transformations
    like PyTorch.transform.

    """
    def __init__(self, ops_list: List[Callable], image: Image):
        """Initialize the pipeline by passing a list of transformations
        to be applied on the supplied image

        Parameters
        ----------
        ops_list: The list of callable ops on the image
        image: The image to transform using this pipeline
        """
        self.ops_list = ops_list
        self.image = image

    def __call__(self, *args, **kwargs):

        if self.ops_list is None or len(self.ops_list) == 0:
            raise ValueError("The ops_list is empty for this pipeline")

        if self.image is None:
            raise ValueError("The source image for this pipeline has not been specified")

        img: Image = self.image
        for op in self.ops_list:
            img = op(img)

        return img
