from cerebrium.logging.base import ConduitLogger
from censius import CensiusClient, ModelType
from tenacity import retry, stop_after_attempt, wait_fixed
from time import time
import numpy as np
from tenacity import retry, stop_after_attempt, wait_fixed


class CensiusLogger(ConduitLogger):
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

        self.tenant_id = platform_authentication["tenant_id"]
        self.project_id = platform_args["project_id"]
        self.training_info = platform_args["training_info"]
        self.model_type = platform_args["model_type"]
        self.client = CensiusClient(api_key=self.api_key, tenant_id=self.tenant_id)

    def check_ready(self, model_version: str, model_name: str) -> str:
        self.model_name = model_name
        self.model_version = model_version
        response = self.client.register_new_model_version(
            model_id=model_name,
            model_version=model_version,
            targets=self.targets,
            features=self.features,
            project_id=self.project_id,
            training_info=self.training_info,
        )
        if str(response) == "Model with the ID does not exist":
            response = self.client.register_model(
                model_id=model_name,
                model_type=self.model_type,
                model_name=model_name,
                model_version=model_version,
                training_info=self.training_info,
                project_id=self.project_id,
                targets=self.targets,
                features=self.features,
            )
            if str(response) != "Model with the ID already exists":
                self.ready = True
            response_msg = (
                f"Model {model_name} already exists with Censius@{self.project_id}."
            )

        elif (
            str(response)
            == "A model with this id and version already exists under this tenant"
        ):
            self.ready = True
            response_msg = f"Model {model_name}@{model_version} already exists with Censius@{self.project_id}"
        elif response.get("version") == model_version:
            self.ready = True
            response_msg = f"Registered new model version {model_name}@{model_version} with Censius@{self.project_id}."
        else:
            response_msg = f"Unable to register new model version for {model_name} with Censius@{self.project_id}."
        return response_msg, self.ready

    @retry(wait=wait_fixed(60), stop=stop_after_attempt(5))
    async def log(self, data: list, predictions: list, prediction_id: str):
        timestamp = round(time()) if self.log_ms else round(time() * 1000)
        feature_dict = {label: data[i] for i, label in enumerate(self.features)}
        prediction_dict = {}
        for i, t in enumerate(self.targets):
            if self.model_type == ModelType.BINARY_CLASSIFICATION:
                prediction_dict[t] = {
                    "label": int(np.argmax(predictions[i])),
                    "confidence": float(np.max(predictions[i])),
                }
            else:
                prediction_dict[t] = {
                    "value": predictions[i],
                }
        response = self.client.log(
            model_id=self.model_name,
            model_version=self.model_version,
            features=feature_dict,
            prediction=prediction_dict,
            timestamp=timestamp,
            prediction_id=prediction_id,
        )
        return response
