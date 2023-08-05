""" Ping a InferenceDeployment """
from __future__ import annotations

from typing import Optional, Union

import requests
from requests import Response

from mcli.api.model.inference_deployment import InferenceDeployment

__all__ = ['ping_inference_deployment']


def ping_inference_deployment(
    deployment: Union[InferenceDeployment, str],
    *,
    timeout: Optional[float] = 10,
) -> dict:
    """Pings an inference deployment that has been launched in the MosaicML platform
    and returns the status of the deployment. The deployment must have a '/ping' endpoint
    defined.
    Arguments:
        deployment:(InferenceDeployment | str): The deployment to check the status of. Can be
            either an InferenceDeployment or a string which is of the form https://<the deployment dns>.
        timeout: Time, in seconds, in which the call should complete. If the call
            takes too long, a TimeoutError will be raised.
    Raises:
        HTTPError: If pinging the endpoint fails
    """
    base_url = f'https://{deployment.public_dns}' if isinstance(deployment, InferenceDeployment) else deployment
    resp: Response = requests.get(url=f'{base_url}/ping', timeout=timeout)
    if resp.ok:
        return resp.json()
    else:
        resp.raise_for_status()
        return {}
