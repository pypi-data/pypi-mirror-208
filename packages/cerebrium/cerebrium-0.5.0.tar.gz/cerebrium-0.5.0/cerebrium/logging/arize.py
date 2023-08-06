from cerebrium.logging.base import ConduitLogger
from arize.pandas.logger import Client
from arize.utils.types import ModelTypes, Environments, Metrics
from tenacity import retry, stop_after_attempt, wait_fixed
from time import time
import numpy as np
import pandas as pd


class ArizeLogger(ConduitLogger):
    def __init__(
        self,
        platform_authentication: dict,
        platform_model_id: str,
        features: list,
        targets: list,
        platform_args: dict,
        log_ms: bool = False,
    ):
        super().__init__(
            platform_authentication,
            platform_model_id,
            features,
            targets,
            platform_args,
            log_ms,
        )

        self.space_key = platform_authentication["space_key"]
        self.api_key = platform_args["api_key"]
        self.model_type = platform_args["model_type"]
        self.features = platform_args["features"]
        self.schema = platform_args["schema"]
        self.metrics_validation = platform_args.get("metrics_validation", [])
        self.environment = platform_args.get("environment", Environments.PRODUCTION)
        self.platform_args = platform_args
        self.client = Client(space_key=self.space_key, api_key=self.api_key)

    def check_ready(self, model_version: str, model_name: str) -> str:
        self.model_name = model_name
        self.model_version = model_version

        return "", True

    @retry(wait=wait_fixed(60), stop=stop_after_attempt(5))
    async def log(self, data: list, predictions: list, prediction_id: str):
        df = {label: data[i] for i, label in enumerate(self.features)}
        df["prediction_id"] = prediction_id

        if self.model_type == ModelTypes.BINARY_CLASSIFICATION:
            df["prediction"] = np.argmax(predictions)

        elif self.model_type == ModelTypes.REGRESSION:
            df["prediction"] = predictions[0]

        elif self.model_type == ModelTypes.SCORE_CATEGORICAL:
            df["prediction_score"] = float(np.max(predictions))
            if "class_labels" in self.platform_args:  ##multi-class classification
                df["prediction"] = self.platform_args["class_labels"][
                    np.argmax(predictions)
                ]

            if "embedding_features" in self.platform_args:
                df["embedding_features"] = self.platform_args["embedding_features"]

        response = self.client.log(
            model_id=self.model_name,
            model_version=self.model_version,
            model_type=self.model_type,
            metrics_validation=self.metrics_validation,
            environment=self.environment,
            dataframe=pd.DataFrame([df], columns=df.keys()),
            schema=self.schema,
            sync=True,
        )
        return response
