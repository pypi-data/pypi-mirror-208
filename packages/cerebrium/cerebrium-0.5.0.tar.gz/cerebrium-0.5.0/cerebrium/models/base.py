from abc import ABC, abstractmethod
from typing import Union, List
from torch import Tensor
from numpy import ndarray
from sklearn.base import BaseEstimator
from torch.nn import Module as TorchModule
from enum import Enum


class ModelType(Enum):
    XGBOOST_CLASSIFIER = "xgboost_classifier"
    XGBOOST_REGRESSOR = "xgboost_regressor"
    TORCH = "torch"
    SKLEARN = "sklearn"
    SKLEARN_CLASSIFIER = "sklearn_classifier"
    ONNX = "onnx"
    SKLEARN_PREPROCESSOR = "sklearn_preprocessor"
    PREBUILT = "prebuilt"
    SPACY = "spacy"
    HUGGINGFACE_PIPELINE = "hf_pipeline"


class BaseModel(ABC):
    def __init__(self, model: Union[BaseEstimator, TorchModule]):
        self.model = model

    @abstractmethod
    def predict(self, input: Union[Tensor, ndarray, List]) -> list:
        pass
