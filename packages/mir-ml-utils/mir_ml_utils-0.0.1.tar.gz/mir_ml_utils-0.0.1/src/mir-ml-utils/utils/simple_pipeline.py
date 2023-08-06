from typing import List, Callable, Any


class SimpleExecutor(object):

    def __init__(self, executor: Callable, *args):
        self.executor = executor
        self.args = args

    def __call__(self, *args, **kwargs) ->Any:
        self.executor(*self.args)


class SimplePipeline(object):
    """The class ImgPipeline.Defines a simple wrapper
    of transformations applied on images. Each transformation
    should expose the __call__(img) function.
    A transformation may be a series of transformations
    like PyTorch.transform.

    """
    def __init__(self, ops_list: List[Callable], item: Any = None):
        """Initialize the pipeline by passing a list of transformations
        to be applied on the supplied image

        Parameters
        ----------
        ops_list: The list of callable ops on the image
        image: The image to transform using this pipeline
        """
        self.ops_list = ops_list
        self.item = item

    def __call__(self, *args, **kwargs):

        if self.ops_list is None or len(self.ops_list) == 0:
            raise ValueError("The ops_list is empty for this pipeline")

        item: Any = self.item
        for op in self.ops_list:
            item = op(item)

        return item