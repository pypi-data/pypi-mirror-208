from cloudpickle import load as pickle_load, dump
from torch.jit import load as torchscript_load
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper
import os
import re
import tempfile
import zipfile
import requests
import json
import enum
from copy import deepcopy

from torch.nn import Module as TorchModule
from torch.cuda import is_available
from numpy import atleast_2d, ndarray
from inspect import getsource, signature

from cerebrium import __version__
from cerebrium.flow import CerebriumFlow, _check_flow_type, _flow_string
from cerebrium.models.base import ModelType
from cerebrium.logging.base import LoggingPlatform
from cerebrium.requests import _cerebrium_request, _poll_deployment_status

REGEX_NAME_PATTERN = "^[a-z0-9-]*$"
API_KEY = None


def _set_api_key(api_key):
    global API_KEY
    API_KEY = api_key


class Hardware(enum.Enum):
    CPU = "cpu"
    GPU = "gpu"
    A10 = "a10"


class Conduit:
    """
    The Conduit class encompasses the logic required to create a computational graph from a given model flow, as well as the logic required to run the graph on a given input.

    Args:
        name (str): The name to deploy the flow under.
        api_key (str): The API key for the Cerebrium account.
        flow (CerebriumFlow): The flow to deploy. This is a list of ModelType, model path and postprocessor tuples, as such:
            [(model_type.TORCH, "model.pt", postprocess_f)]
        hardware (Hardware): The hardware to deploy the model on.
    """

    def __init__(
        self,
        name: str = "",
        api_key: str = "",
        flow: CerebriumFlow = [],
        hardware: Hardware = None,
        from_json: str = "",
    ):
        if not from_json:
            assert name != "" and api_key != ""
            # Check that the flow name is valid
            if len(name) > 20:
                raise ValueError("Conduit name must be less than 20 characters")
            if not bool(re.match(REGEX_NAME_PATTERN, name)):
                raise ValueError(
                    "Conduit name can only contain lowercase alphanumeric characters and hyphens"
                )
            self.name = name
            self.api_key = api_key
            if flow is not None:
                self.flow = _check_flow_type(flow)
            self.logger_configs = {}
            self._processors = None
        else:
            with open(from_json, "r") as f:
                config = json.load(f)
                self.name = config["name"]
                self.api_key = config["api_key"]
                self.flow = config["flow"]
                self.logger_configs = config["logger_configs"]
                self._processors = config["processors"]
                # Set correct ModelTypes in flow
                for i, (model_type, model_initialization, processors) in enumerate(
                    self.flow
                ):
                    self.flow[i] = (
                        ModelType(model_type),
                        model_initialization,
                        processors,
                    )
                hardware = Hardware(config["hardware"])
        _set_api_key(self.api_key)
        self.graph = []
        self.ready = False
        self.loggers = {}
        if hardware:
            self.hardware = hardware
        else:
            self.hardware = self._determine_hardware()
        self.device = (
            "cuda" if self.hardware == Hardware.GPU and is_available() else "cpu"
        )

    def _determine_hardware(self):
        # Set the default hardware to GPU if the flow contains a Torch, ONNX or HuggingFace model
        if any(
            [
                model_type
                in [ModelType.TORCH, ModelType.ONNX, ModelType.HUGGINGFACE_PIPELINE]
                for model_type, _, _ in self.flow
            ]
        ):
            return Hardware.GPU
        else:
            return Hardware.CPU

    def load(self, directory: str = "/cache/", direct_from_flow: bool = False):
        """
        Load the Conduit components from the stored Model Flow into the computation graph.

        Args:
            directory (str): The directory to load the Conduit components from.
        """
        from sklearn.base import ClassifierMixin, RegressorMixin, BaseEstimator

        if self.flow == []:
            raise ValueError("Conduit is empty. Please add models to the Conduit flow.")
        else:
            for model_type, model_initialization, _ in self.flow:
                # Use correct path
                if direct_from_flow:
                    model_initialization = os.path.abspath(model_initialization)
                elif (
                    model_type != ModelType.PREBUILT
                    and model_type != ModelType.HUGGINGFACE_PIPELINE
                ):
                    model_initialization = (
                        directory + model_initialization.split("/")[-1]
                    )
                else:
                    pass

                # Torch
                if model_type == ModelType.TORCH:
                    from cerebrium.models.torch import TorchModel

                    if model_initialization.endswith(".pt"):
                        model: TorchModule = torchscript_load(model_initialization)
                    else:
                        with open(model_initialization, "rb") as f:
                            model: TorchModule = pickle_load(f)
                    model.to(self.device)
                    self.graph.append(TorchModel(model))

                # ONNX
                elif model_type == ModelType.ONNX:
                    from cerebrium.models.onnx import OnnxModel
                    from onnxruntime import InferenceSession

                    providers = (
                        ["CUDAExecutionProvider", "CPUExecutionProvider"]
                        if self.device == "cuda"
                        else ["CPUExecutionProvider"]
                    )
                    model = InferenceSession(
                        model_initialization,
                        providers=providers,
                    )
                    self.graph.append(OnnxModel(model))

                # Spacy
                elif model_type == ModelType.SPACY:
                    from cerebrium.models.spacy import SpacyModel
                    from spacy import load as spacy_load

                    model = spacy_load(model_initialization)
                    self.graph.append(SpacyModel(model))

                # XGBoost
                elif model_type == ModelType.XGBOOST_CLASSIFIER:
                    from cerebrium.models.sklearn import SKClassifierModel
                    from xgboost import XGBClassifier

                    if model_initialization.endswith("json"):
                        model = XGBClassifier()
                        model.load_model(model_initialization)
                    else:
                        with open(model_initialization, "rb") as f:
                            model: XGBClassifier = pickle_load(f)
                    self.graph.append(SKClassifierModel(model))
                elif model_type == ModelType.XGBOOST_REGRESSOR:
                    from cerebrium.models.sklearn import SKRegressorModel
                    from xgboost import XGBRegressor

                    if model_initialization.endswith("json"):
                        model = XGBRegressor()
                        model.load_model(model_initialization)
                    else:
                        with open(model_initialization, "rb") as f:
                            model: XGBRegressor = pickle_load(f)
                    self.graph.append(SKRegressorModel(model))

                # Scikit-Learn Interface
                elif model_type == ModelType.SKLEARN_CLASSIFIER:
                    from cerebrium.models.sklearn import SKClassifierModel

                    with open(model_initialization, "rb") as f:
                        model: ClassifierMixin = pickle_load(f)
                    self.graph.append(SKClassifierModel(model))
                elif model_type == ModelType.SKLEARN:
                    from cerebrium.models.sklearn import SKRegressorModel

                    with open(model_initialization, "rb") as f:
                        model: RegressorMixin = pickle_load(f)
                    self.graph.append(SKRegressorModel(model))
                elif model_type == ModelType.SKLEARN_PREPROCESSOR:
                    from cerebrium.models.sklearn import SKPreprocessorModel

                    with open(model_initialization, "rb") as f:
                        model: BaseEstimator = pickle_load(f)
                    self.graph.append(SKPreprocessorModel(model))

                # HuggingFace Pipeline
                elif model_type == ModelType.HUGGINGFACE_PIPELINE:
                    from cerebrium.models.hf_pipeline import HFPipeline
                    from transformers.pipelines import pipeline

                    model = HFPipeline(pipeline(**model_initialization))
                    self.graph.append(model)

            # If there are processors, create a processors.py file with the respective processors
            # Save the processors.py file in the /usr/local/lib/python3.10/dist-packages/conduit_processors directory
            if self._processors:
                if not os.path.exists(
                    ".venv/lib/python3.10/site-packages/conduit_processors"
                ):
                    os.makedirs(
                        ".venv/lib/python3.10/site-packages/conduit_processors"
                    )
                # Create the processors.py file
                with open(
                    ".venv/lib/python3.10/site-packages/conduit_processors/processors.py",
                    "w",
                ) as f:
                    f.write(
                        "from cerebrium import save, get, delete, upload\n"
                        "import numpy as np\n"
                        "import pandas as pd\n"
                        "import torch\n"
                    )
                    for processors in self._processors:
                        if processors["pre"]:
                            source = processors["pre"]
                            f.write(source)
                        if processors["post"]:
                            source = processors["post"]
                            f.write(source)
                # Create the __init__.py file
                with open(
                    ".venv/lib/python3.10/site-packages/conduit_processors/__init__.py",
                    "w",
                ) as f:
                    f.write("from .processors import *\n")

            self.ready = True

    def run(self, data: list, files: list = []):
        """
        Run the Conduit on the given input with the stored computational graph.

        Args:
            data (list): The input data to run the Conduit on.
        """
        from torch import Tensor

        if self._processors:
            # List files in working directory
            files = os.listdir()
            import conduit_processors

        if not self.ready:
            return "Conduit not ready. Conduit components have not been loaded."
        else:
            # If there is no initial pre-processor, convert the data accordingly
            if not self.flow[0][2].get("pre", False):
                if self.flow[0][0] == ModelType.TORCH:
                    data = Tensor(atleast_2d(data)).to(self.device)
                elif self.flow[0][0] == ModelType.ONNX:
                    if isinstance(data, list):
                        data = data[0]
                    else:
                        pass
                elif self.flow[0][0] == ModelType.HUGGINGFACE_PIPELINE:
                    pass
                elif self.flow[0][0] == ModelType.SPACY:
                    data = data[0]
                elif any([isinstance(d, bytes) for d in data]):
                    pass
                else:
                    data = atleast_2d(data)

            # Set input data
            input_data = data

            for (model_type, _, processors), (model) in zip(self.flow, self.graph):
                # Run the preprocessor
                preprocessor = processors.get("pre", None)
                postprocessor = processors.get("post", None)
                if preprocessor:
                    if self._processors:
                        preprocessor = getattr(conduit_processors, preprocessor)
                    sig = signature(preprocessor)
                    if len(sig.parameters) == 1:
                        data = preprocessor(data)
                    elif len(sig.parameters) == 2:
                        data = preprocessor(data, files)

                # Ensure that the input data is the correct type
                if model_type == ModelType.TORCH and not isinstance(data, Tensor):
                    data = Tensor(data).to(self.device)
                elif model_type != ModelType.TORCH and isinstance(data, Tensor):
                    data = data.detach().to("cpu").numpy()

                # Run the model
                data = model.predict(data)

                # Run the postprocessor
                if postprocessor:
                    if self._processors:
                        postprocessor = getattr(conduit_processors, postprocessor)
                    sig = signature(postprocessor)
                    if len(sig.parameters) == 1:
                        data = postprocessor(data)
                    elif len(sig.parameters) == 2:
                        data = postprocessor(data, input_data)
                    else:
                        data = postprocessor(data, input_data, files)

            # Ensure that final output is a list
            if isinstance(data, Tensor):
                data = data.detach().to("cpu").numpy().tolist()
            elif isinstance(data, ndarray):
                data = data.tolist()
            elif not isinstance(data, list) and not isinstance(data, dict):
                data = [data]
            return data

    def add_model(self, model_type, model_initialization, postprocessor=None):
        """
        Add a model to the Conduit's computational flow.
        """
        temp_flow = self.flow
        temp_flow.append((model_type, model_initialization, postprocessor))
        self.flow = _check_flow_type(temp_flow)
        self._determine_hardware()

    def add_logger(
        self,
        platform: LoggingPlatform,
        platform_authentication: dict,
        features: list,
        targets: list,
        platform_args: dict = {},
        log_ms: bool = False,
    ):
        """
        Add a logger to the Conduit's computational flow.

        Args:
            platform (LoggingPlatform): The logging platform to use.
            platform_authentication (dict): The authentication credentials for the logging platform.
            features (list): The features to log.
            targets (list): The targets to log.
            platform_args (dict, optional): Any additional arguments to pass to the logger. Defaults to {}.
            log_ms (bool, optional): Whether to log the milliseconds of the input data. Defaults to False.
        """
        platform = platform.value
        self.logger_configs[platform] = {
            "platform_authentication": platform_authentication,
            "features": features,
            "targets": targets,
            "platform_args": platform_args,
            "log_ms": log_ms,
        }

    def setup_loggers(self):
        """
        Setup the loggers for the Conduit.
        """
        for platform, config in self.logger_configs.items():
            if platform == "Censius":
                from cerebrium.logging.censius import CensiusLogger
                from censius import ModelType

                # If there are processors, set the model type to the last model in the flow
                if self._processors:
                    self.logger_configs[platform]["platform_args"]["model_type"] = eval(
                        config[platform]["platform_args"]["model_type"]
                    )
                self.loggers["Censius"] = CensiusLogger(
                    config["platform_authentication"],
                    self.name,
                    config["features"],
                    config["targets"],
                    config["platform_args"],
                    config["log_ms"],
                )
            elif platform == "Arize":
                from cerebrium.logging.arize import ArizeLogger
                from arize.utils.types import (
                    ModelTypes,
                    Metrics,
                    Schema,
                    Embedding,
                )

                # If there are processors, recreate the model type, metrics, schema, and embedding objects
                if self._processors:
                    from pandas import Series

                    self.logger_configs[platform]["platform_args"]["model_type"] = eval(
                        config[platform]["platform_args"]["model_type"]
                    )
                    self.logger_configs[platform]["platform_args"]["metrics"] = [
                        eval(x) for x in config[platform]["platform_args"]["metrics"]
                    ]
                    self.logger_configs[platform]["platform_args"]["schema"] = Schema(
                        **config[platform]["platform_args"]["schema"]
                    )
                    if config[platform]["platform_args"].get("embedding", None):
                        for feature in config[platform]["platform_args"]["embedding"]:
                            self.logger_configs[platform]["platform_args"]["embedding"][
                                feature
                            ] = Embedding(
                                data=config[platform]["platform_args"]["embedding"][
                                    feature
                                ]["data"],
                                vector=Series(
                                    config[platform]["platform_args"]["embedding"][
                                        feature
                                    ]["vector"]
                                ),
                            )
                self.loggers["Arize"] = ArizeLogger(
                    config["platform_authentication"],
                    self.name,
                    config["features"],
                    config["targets"],
                    config["platform_args"],
                    config["log_ms"],
                )

    def _jsonify_loggers(self):
        """
        Serialize the loggers to JSON for the Conduit.
        """
        logger_configs = {}
        for platform, config in self.logger_configs.items():
            if platform == "Censius":
                from censius import ModelType

                logger_configs[platform] = deepcopy(config)
                if (
                    config["platform_args"]["model_type"]
                    == ModelType.BINARY_CLASSIFICATION
                ):
                    logger_configs[platform]["platform_args"][
                        "model_type"
                    ] = "ModelType.BINARY_CLASSIFICATION"
                else:
                    logger_configs[platform]["platform_args"][
                        "model_type"
                    ] = "ModelType.REGRESSION"
            elif platform == "Arize":
                logger_configs[platform] = deepcopy(config)
                logger_configs[platform]["platform_args"]["model_type"] = str(
                    config["platform_args"]["model_type"]
                )
                logger_configs[platform]["platform_args"]["metric"] = [
                    str(x) for x in config["platform_args"]["metric"]
                ]
                logger_configs[platform]["platform_args"]["schema"] = {
                    "prediction_id_column_name": config["platform_args"]["schema"][
                        "prediction_id_column_name"
                    ],
                    "prediction_label_column_name": config["platform_args"]["schema"][
                        "prediction_label_column_name"
                    ],
                    "feature_column_names": config["platform_args"]["schema"][
                        "feature_column_names"
                    ],
                    "tags_column_names": config["platform_args"]["schema"][
                        "tags_column_names"
                    ],
                }
                if config["platform_args"].get("embedding_features", None):
                    logger_configs[platform]["platform_args"][
                        "embedding_features"
                    ] = config["platform_args"]["embedding_features"]
                    for feature in logger_configs[platform]["platform_args"][
                        "embedding_features"
                    ]:
                        logger_configs[platform]["platform_args"]["embedding_features"][
                            feature
                        ] = {
                            "data": logger_configs[platform]["platform_args"][
                                "embedding_features"
                            ][feature]["data"],
                            "vector": logger_configs[platform]["platform_args"][
                                "embedding_features"
                            ][feature]["vector"].tolist(),
                        }

        return logger_configs

    def create_json_config(self, filename):
        """
        Return the Conduit's configuration as a JSON string.

        Returns:
            str: The Conduit's configuration as a JSON string.
        """

        def get_function_names(processors):
            names = {}
            if "pre" in processors:
                names["pre"] = processors["pre"].__name__
            else:
                names["pre"] = None
            if "post" in processors:
                names["post"] = processors["post"].__name__
            else:
                names["post"] = None
            return names

        json_flow = [
            (model_type.value, model_initialization, get_function_names(processors))
            for model_type, model_initialization, processors in self.flow
        ]
        with open(filename, "w") as f:
            json.dump(
                {
                    "name": self.name,
                    "flow": json_flow,
                    "api_key": self.api_key,
                    "logger_configs": self._jsonify_loggers(),
                    "processors": [
                        {
                            "pre": None
                            if p[2].get("pre", None) is None
                            else getsource(p[2]["pre"]),
                            "post": None
                            if p[2].get("post", None) is None
                            else getsource(p[2]["post"]),
                        }
                        for p in self.flow
                    ],
                    "hardware": self.hardware.value,
                },
                f,
                indent=2,
            )

    def _upload(self, url):
        """
        Upload the Conduit to Cerebrium.

        Args:
            url (str): The upload URL.

        Returns:
            dict ('status_code': int, 'data': dict): The response code and data. 'data' contains the flow token if successful.
        """
        if self.flow == []:
            raise ValueError("Conduit is empty. Please add models to the Conduit.")
        else:
            # Clear the graph
            if self.ready:
                print("Clearing the Conduit graph...")
                self.graph = []
                self.ready = False
            # Clear the loggers
            if self.loggers:
                print("Clearing the Conduit loggers...")
                self.loggers = {}
            self.graph = []
            self.ready = False
            # Create a temporary directory to store the Conduit zip
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create a zip file of the Conduit, writing the model files and Conduit object to the zip
                with zipfile.ZipFile(tmpdir + f"/{self.name}.zip", "w") as zip:
                    for model_type, model_initialization, _ in self.flow:
                        if model_type != ModelType.HUGGINGFACE_PIPELINE:
                            true_path = os.path.abspath(model_initialization)
                            zip.write(true_path, os.path.basename(true_path))
                            ## If the model is a spaCy model, write all the folder contents to the zip
                            ## This is necessary because spaCy models are directories
                            if model_type == ModelType.SPACY:
                                for root, _, files in os.walk(true_path):
                                    for file in files:
                                        directory = os.path.basename(root)
                                        if root == true_path:
                                            directory = ""
                                        else:
                                            directory = "/" + os.path.basename(root)
                                        zip.write(
                                            os.path.join(root, file),
                                            os.path.join(
                                                f"{os.path.basename(true_path)}{directory}",
                                                file,
                                            ),
                                        )
                    self.create_json_config("conduit.json")
                    zip.write("conduit.json")
                # Upload the Conduit zip, chunking with tqdm for progress bar
                with open(tmpdir + f"/{self.name}.zip", "rb") as f:
                    headers = {
                        "Content-Type": "application/zip",
                    }
                    with tqdm(
                        total=os.path.getsize(tmpdir + f"/{self.name}.zip"),
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        colour="#EB3A6F",
                    ) as pbar:
                        wrapped_f = CallbackIOWrapper(pbar.update, f, "read")
                        response = requests.put(
                            url,
                            headers=headers,
                            data=wrapped_f,
                            timeout=60,
                            stream=True,
                        )
                    data = {} if not response.text else json.loads(response.text)
                    return {"status_code": response.status_code, "data": data}

    def deploy(self, dry_run=False):
        """
        Deploy the Conduit to Cerebrium.

        Returns:
            dict ('status_code': int, 'data': dict): The response code and data. 'data' contains the flow token if successful.
        """
        # Deploy the conduit
        if not dry_run:
            # Check that the user is authenticated
            upload_url_response = _cerebrium_request(
                "getUploadUrl",
                self.api_key,
                payload={
                    "name": self.name,
                    "cerebriumVersion": __version__,
                    "hardware": self.hardware.value,
                },
                enable_spinner=(
                    True,
                    ("Authenticating...", "Authenticated with Cerebrium!"),
                ),
            )
            upload_url = upload_url_response["data"]["uploadUrl"]

            # If Prebuilt model, register with modal
            if self.flow[0][0] == ModelType.PREBUILT:
                print("Registering with Cerebrium...")
                prebuilt_model_response = _cerebrium_request(
                    "pre-built-model",
                    self.api_key,
                    payload={
                        "arguments": {
                            "name": self.name,
                            "externalId": self.flow[0][1],
                            "modelType": _flow_string(self.flow),
                        }
                    },
                    enable_spinner=(
                        True,
                        ("Registering with Cerebrium...", "Registered with Cerebrium!"),
                    ),
                )
                endpoint = prebuilt_model_response["data"]["internalEndpoint"]
                print("🌍 Endpoint:", endpoint)
                return endpoint
            else:
                # Upload the conduit artefacts to Cerebrium
                print("⬆️  Uploading conduit artefacts...")
                self._upload(upload_url)
                print("✅ Conduit artefacts uploaded successfully.")
                endpoint = _poll_deployment_status(self.name, self.api_key)
                print("🌍 Endpoint:", endpoint)
                return endpoint
        else:
            if self.flow[0][0] == ModelType.PREBUILT:
                raise NotImplementedError("Dry run not supported for prebuilt models")
            self.load(direct_from_flow=True)
            return self
