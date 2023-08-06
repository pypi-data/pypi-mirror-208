from enum import Enum
from abc import ABC, abstractmethod


class LoggingPlatform(Enum):
    CENSIUS = "Censius"
    ARIZE = "Arize"


class ConduitLogger(ABC):
    def __init__(
        self,
        platform_authentication: dict,
        platform_model_id: str,
        features: list,
        targets: list,
        platform_args: dict,
        log_ms: bool = False,
    ):
        self.api_key = platform_authentication["api_key"]
        self.project_id = platform_model_id
        self.features = features
        self.targets = targets
        self.platform_args = platform_args
        self.log_ms = log_ms
        self.ready = False

    @abstractmethod
    def log(self, **kwargs):
        pass
