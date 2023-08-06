import requests
import json
import os

from typing import Tuple
from tenacity import retry, stop_after_delay, wait_fixed
from yaspin import yaspin
from yaspin.spinners import Spinners
from cerebrium.errors import CerebriumRequestError, CerebriumDeploymentError


ENV = os.getenv("DEVELOPMENT_ENV", "prod")
if ENV == "dev":
    print("Using development environment")
    BASE_CEREBRIUM_URL = "https://dev-rest-api.cerebrium.ai"
else:
    BASE_CEREBRIUM_URL = "https://rest-api.cerebrium.ai"


def _check_payload(method: str, payload: dict) -> bool:
    """
    Check that the payload for a given method is valid.

    Args:
        payload (dict): The payload to check.

    Returns:
        bool: True if the payload is valid, False otherwise.
    """
    if method == "getUploadUrl":
        if "name" not in payload:
            raise ValueError(f"Payload for '{method}' must contain 'name' key")
    elif method == "pre-built-model":
        if (
            "name" not in payload["arguments"]
            or "externalId" not in payload["arguments"]
            or "modelType" not in payload["arguments"]
        ):
            raise ValueError(
                f"Payload for '{method}' must contain 'name', 'externalId' and 'modelType' keys"
            )
    elif method == "checkDeploymentStatus":
        if "name" not in payload["arguments"]:
            raise ValueError(f"Payload for '{method}' must contain 'name' key")


def _cerebrium_request(
    method: str,
    api_key: str,
    payload: dict = None,
    enable_spinner: Tuple[bool, Tuple[str, str]] = (False, ("", "")),
) -> dict:
    """
    Make a request to the Cerebrium API.

    Args:
        method (str): The server method to use.
        api_key (str): The API key for the Cerebrium account.
        payload (dict): The payload to send with the request.
        enable_spinner (List[bool, List[str, str]]): A list containing a boolean to enable the spinner and a list containing the spinner text and spinner type.

    Returns:
        dict ('status_code': int, 'data': dict): The response code and data.
    """

    headers = {"Authorization": api_key, "ContentType": "application/json"}
    url = f"{BASE_CEREBRIUM_URL}/{method}"

    # Make a request to the Cerebrium API
    @retry(stop=stop_after_delay(60), wait=wait_fixed(8))
    def _request():
        if payload is not None:
            _check_payload(method, payload)
            response = requests.post(
                url, headers=headers, data=json.dumps(payload), timeout=30
            )
        else:
            response = requests.get(url, headers=headers, timeout=30)
        return {"status_code": response.status_code, "data": json.loads(response.text)}

    if enable_spinner[0]:
        with yaspin(Spinners.arc, text=enable_spinner[1][0], color="magenta"):
            response = _request()
        if response["status_code"] == 200:
            print(f"✅ {enable_spinner[1][1]}")
        else:
            print(f"✗ {enable_spinner[1][1]}")
            raise CerebriumRequestError(
                response["status_code"],
                method,
                response["data"],
            )
    else:
        response = _request()
    return response


@retry(stop=stop_after_delay(60), wait=wait_fixed(2))
def _poll_deployment_status(conduit_name: str, api_key: str) -> str:
    """
    Poll the deployment status of a conduit.

    Args:
        conduit_name (str): The name of the conduit to check the status of.
        api_key (str): The API key for the Cerebrium account.

    Returns:
        str: The endpoint of the deployed model.
    """
    # Check the status of the deployment by polling the Cerebrium API for deployment status
    with yaspin(
        spinner=Spinners.arc, text="Checking deployment status...", color="magenta"
    ) as spinner:
        response = _cerebrium_request(
            "checkDeploymentStatus",
            api_key,
            payload={"arguments": {"name": conduit_name}},
        )
    if response["data"]["status"] == "deployed":
        endpoint = response["data"]["endpoint"]
        print("✅ Conduit deployed!")
        return endpoint
    elif response["data"]["status"] == "failed":
        print("❌ Conduit deployment failed.")
        raise CerebriumDeploymentError(response["data"]["failureMessage"])
    else:
        print("⏳ Conduit deployment in progress...")
        raise CerebriumDeploymentError(
            "Deployment Not Complete. Your conduit might be large and take longer to deploy. Please try again later."
        )
