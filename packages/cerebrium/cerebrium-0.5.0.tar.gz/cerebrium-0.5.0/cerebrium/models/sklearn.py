from torch import Tensor
from numpy import atleast_2d, ndarray
from typing import Union, List
from cerebrium.models.base import BaseModel


class SKClassifierModel(BaseModel):
    def predict(self, input: Union[Tensor, ndarray, List]) -> list:
        if not isinstance(input, ndarray):
            if isinstance(input, Tensor):
                input = input.detach().cpu().numpy()
            input = atleast_2d(input)
        return self.model.predict_proba(input)


class SKRegressorModel(BaseModel):
    def predict(self, input: Union[Tensor, ndarray, List]) -> list:
        if not isinstance(input, ndarray):
            if isinstance(input, Tensor):
                input = input.detach().cpu().numpy()
            input = atleast_2d(input)
        return self.model.predict(input)


class SKPreprocessorModel(BaseModel):
    def predict(self, input: Union[Tensor, ndarray, List]) -> list:
        if not isinstance(input, ndarray):
            if isinstance(input, Tensor):
                input = input.detach().cpu().numpy()
            input = atleast_2d(input)
        return self.model.transform(input)
