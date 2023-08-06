"""module exceptions. Specifies various
exception classes used around the mir-engine

"""


class InvalidPILImageMode(Exception):
    def __init__(self, mode: str):
        """Constructor
        Parameters
        ----------
        mode: The mode of the PIL.Image
        """

        self.message: str = "Mode {0} is an invalid PIL.Image mode".format(mode)

    def __str__(self):
        return self.message


class InvalidLabel(Exception):
    def __init__(self, label: str):
        self.message: str = "Label value {0} is invalid".format(label)

    def __str__(self):
        return self.message


class SizeMismatchException(Exception):
    def __init__(self, size1: int, size2: int):
        self.message: str = "Size {0} != {1}".format(size1, size2)

    def __str__(self):
        return self.message


class FixMeException(Exception):
    def __init__(self, mesage: str):
        self.message = mesage

    def __str__(self):
        return self.message


class InvalidModelType(Exception):
    def __init__(self, model: str, model_type: str):
        self.message = f"Model {model} is not of type {str}"

    def __str__(self):
        return self.message
