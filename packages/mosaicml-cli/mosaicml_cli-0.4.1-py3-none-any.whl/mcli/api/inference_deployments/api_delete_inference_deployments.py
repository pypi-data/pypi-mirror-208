""" Delete a deployment. """
from __future__ import annotations

from concurrent.futures import Future
from typing import List, Optional, Union, overload

from typing_extensions import Literal

from mcli.api.engine.engine import get_return_response, run_plural_mapi_request
from mcli.api.model.inference_deployment import InferenceDeployment
from mcli.config import MCLIConfig

QUERY_FUNCTION = 'deleteInferenceDeployments'
VARIABLE_DATA_NAME = 'getInferenceDeploymentsData'
QUERY = f"""
mutation DeleteInferenceDeployments(${VARIABLE_DATA_NAME}: GetInferenceDeploymentsInput!) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}) {{
    id
    name
    inferenceDeploymentInput
    originalInferenceDeploymentInput
    status
    createdAt
    updatedAt
    deletedAt
    publicDNS
    createdByEmail
  }}
}}"""

__all__ = ['delete_inference_deployments']


@overload
def delete_inference_deployments(
    deployments: Union[List[str], List[InferenceDeployment]],
    *,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> List[InferenceDeployment]:
    ...


@overload
def delete_inference_deployments(
    deployments: Union[List[str], List[InferenceDeployment]],
    *,
    timeout: Optional[float] = None,
    future: Literal[True] = True,
) -> Future[List[InferenceDeployment]]:
    ...


def delete_inference_deployments(
    deployments: Union[List[str], List[InferenceDeployment]],
    *,
    timeout: Optional[float] = 10,
    future: bool = False,
):
    """Delete a list of inference deployments in the MosaicML Cloud
    Any deployments that are currently running will first be stopped.
    Args:
        deploymnets: A list of inference deployments or inference deployment names to delete
        timeout: Time, in seconds, in which the call should complete. If the call
            takes too long, a TimeoutError will be raised. If ``future`` is ``True``, this
            value will be ignored.
        future: Return the output as a :type concurrent.futures.Future:. If True, the
            call to `delete_inference_deployments` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the :type InferenceDeployment: output, use ``return_value.result()``
            with an optional ``timeout`` argument.
    Returns:
        A list of :type InferenceDeployment: for the inference deployments that were deleted
    """
    # Extract run names
    deployment_names = [d.name if isinstance(d, InferenceDeployment) else d for d in deployments]

    filters = {}
    if deployment_names:
        filters['name'] = {'in': deployment_names}

    variables = {VARIABLE_DATA_NAME: {'filters': filters}}

    cfg = MCLIConfig.load_config(safe=True)
    if cfg.user_id:
        variables[VARIABLE_DATA_NAME]['entity'] = {
            'userIds': [cfg.user_id],
        }

    response = run_plural_mapi_request(
        query=QUERY,
        query_function=QUERY_FUNCTION,
        return_model_type=InferenceDeployment,
        variables=variables,
    )

    return get_return_response(response, future=future, timeout=timeout)
