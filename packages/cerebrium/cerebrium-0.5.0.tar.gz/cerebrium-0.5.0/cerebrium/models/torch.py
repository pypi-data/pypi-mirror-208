from torch import tensor, Tensor
from numpy import ndarray
from typing import Union, List
from cerebrium.models.base import BaseModel


class TorchModel(BaseModel):
    def predict(self, input: Union[Tensor, ndarray, List]) -> list:
        if not isinstance(input, Tensor):
            input = tensor(input)
        return self.model(input)
