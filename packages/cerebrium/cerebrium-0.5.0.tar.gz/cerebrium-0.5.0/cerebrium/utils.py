from typing import Union
from numpy import ndarray
from torch import Tensor


def _convert_input_data(data: Union[list, ndarray, Tensor]) -> list:
    """
    Convert the input data to a list.

    Args:
        data (Union[list, ndarray, Tensor]): The data to convert.

    Returns:
        list: The converted data as a python list.
    """

    if isinstance(data, ndarray) or isinstance(data, Tensor):
        return data.tolist()
    else:
        return data
