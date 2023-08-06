""" Predict on an Inference Deployment """
from __future__ import annotations

from typing import Any, Dict, Optional, Union

import requests
from requests import Response

from mcli import config
from mcli.api.model.inference_deployment import InferenceDeployment

__all__ = ['predict']


def predict(
    deployment: Union[InferenceDeployment, str],
    inputs: Dict[str, Any],
    *,
    timeout: Optional[float] = 20,
) -> dict:
    """Sends input to \'/predict\' endpoint of an inference deployment on the MosaicML
    platform. Runs prediction on input and returns output produced by the model.
    Arguments:
        deployment (InferenceDeployment | str): The deployment to make a prediction with.
            Can be either an InferenceDeployment object to send or a string which is of
            the form https://<the deployment dns>.
        input: Input data to run prediction on in the form of dictionary
        timeout: Time, in seconds, in which the call should complete. If the call
            takes too long, a TimeoutError will be raised.
    Raises:
        HTTPError: If sending the request to the endpoint fails
    """
    conf = config.MCLIConfig.load_config(safe=True)
    api_key = conf.api_key
    headers = {
        'authorization': api_key,
    }
    base_url = f'https://{deployment.public_dns}' if isinstance(deployment, InferenceDeployment) else deployment
    resp: Response = requests.post(url=f'{base_url}/predict', timeout=timeout, json=inputs, headers=headers)
    if resp.ok:
        return resp.json()
    else:
        resp.raise_for_status()
        return {}
