from cerebrium.flow import CerebriumFlow
from cerebrium.conduit import Conduit
from cerebrium.utils import _convert_input_data

import requests
import json
from typing import Union, List
import boto3
import os
from uuid import uuid4

from numpy import ndarray
from torch import Tensor
from cerebrium.requests import _cerebrium_request, ENV

IS_SERVER = os.getenv("IS_SERVER", "false")
_objects = {}


def upload(file_name):
    # Upload a file to Cerebrium S3 and return a URL to the file
    from cerebrium.conduit import API_KEY

    if API_KEY and IS_SERVER == "true":
        s3_client = boto3.client("s3")
        id = str(uuid4())
        s3_client.upload_file(file_name, f"cerebrium-file-storage-{ENV}", id)
        # Generate presigned URL to the file
        url = _cerebrium_request(
            method="getFileUrl",
            api_key=API_KEY,
            payload={"file_name": id},
        )
        return url
    else:
        return file_name


def save(name: str, obj: object) -> None:
    """
    Save a Python objec from the current scope to persistent memory so that it can be accessed by processing functions.

    Args:
        name (str): The name to save the object under.
        obj (object): The object to save. This can be any Python object, but must be contained within the scope of the function.
    """
    _objects[name] = obj


def get(name: str) -> None:
    """
    Get a Python object from persistent memory.

    Args:
        name (str): The name of the object to get.

    Returns:
        object: The object saved under the given name.
    """
    try:
        return _objects[name]
    except KeyError as error:
        raise NameError(f"Object '{name}' not found in persistent memory.") from error


def delete(name: str) -> None:
    """
    Delete a Python object from persistent memory.
    """
    try:
        del _objects[name]
    except KeyError as error:
        raise NameError(f"Object '{name}' not found in persistent memory.") from error


def model_api_request(
    model_endpoint: str,
    data: Union[list, ndarray, Tensor],
    api_key: str,
    files: List[bytes] = None,
) -> dict:
    """
    Make a request to the Cerebrium model API.

    Args:
        model_endpoint (str): The endpoint of the model to make a request to.
        data (list): The data to send to the model.

    Returns:
        dict ('status_code': int, 'data': dict): The response code and data.
    """
    payload = _convert_input_data(data)
    headers = {
        "Authorization": api_key,
    }
    if files is not None:
        byte_files = {f"file{i}": (f, open(f, "rb")) for i, f in enumerate(files)}
        byte_files["data"] = (None, json.dumps(payload), "application/json")
        response = requests.request(
            "POST", model_endpoint, headers=headers, timeout=30, files=byte_files
        )
    else:
        payload = json.dumps(payload)
        headers["Content-Type"] = "application/json"
        response = requests.request(
            "POST", model_endpoint, headers=headers, data=payload, timeout=30
        )
    return {"status_code": response.status_code, "data": json.loads(response.text)}


def deploy(
    model_flow: CerebriumFlow,
    name: str,
    api_key: str,
    dry_run=False,
    loggers=[],
    hardware=None,
) -> str:
    """
    Deploy a model to Cerebrium.

    Args:
        model_flow (CerebriumFlow): The flow to deploy. This is a list of ModelType, model path and postprocessor tuples, as such:
            [(ModelType.TORCH, "model.pt", postprocess_f)]
        name (str): The name to deploy the flow under.
        api_key (str): The API key for the Cerebrium account.
        dry_run (bool): Whether to run the deployment in dry-run mode.
            If True, the model will not be deployed, and deploy will return a flow function which can be used to test with.
        logger (dict): A logger configuration used to create logger which will log ML stats to a metrics platform.
        hardware (Hardware): The hardware to deploy the model on. Can be either "cpu" or "gpu".

    Returns:
        str: The newly deployed REST endpoint. If dry_run is True, a flow function will be returned instead.
    """
    # Check that the flow is valid and create the Conduit
    conduit = Conduit(name, api_key, model_flow, hardware)
    if loggers != []:
        for logger in loggers:
            conduit.add_logger(**logger)
    return conduit.deploy(dry_run=dry_run)
