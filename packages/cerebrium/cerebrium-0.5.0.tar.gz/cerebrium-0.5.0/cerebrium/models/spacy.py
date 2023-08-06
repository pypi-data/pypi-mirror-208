from torch import Tensor
from numpy import atleast_2d, ndarray
from typing import Union, List
from cerebrium.models.base import BaseModel


class SpacyModel(BaseModel):
    def predict(self, input: str) -> any:
        return self.model(input)
