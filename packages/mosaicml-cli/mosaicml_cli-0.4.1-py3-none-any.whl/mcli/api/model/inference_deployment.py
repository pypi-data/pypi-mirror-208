"""GraphQL representaion of Deployment"""
from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict, Optional, Tuple

from mcli.api.exceptions import MAPIException
from mcli.api.schema.generic_model import DeserializableModel, convert_datetime
from mcli.models.inference_deployment_config import FinalInferenceDeploymentConfig, InferenceDeploymentConfig


@dataclass
class InferenceDeployment(DeserializableModel):
    """A deployment that has been launched on the MosaicML Cloud
    
    Args:
        deployment_uid (`str`): Unique identifier for the deployment
        name (`str`): User-defined name of the deployment
        status (:class:`~mcli.utils.utils_deployment_status.DeploymentStatus`): Status of the deployment
        at a moment in time
        created_at (`datetime`): Date and time when the deployment was created
        updated_at (`datetime`): Date and time when the deployment was last updated
        config (:class:`~mcli.models.deployment_config.DeploymentConfig`): The
            :class:`deployment configuration <mcli.models.deployment_config.DeploymentConfig>` that was
            used to launch to the deployment
    """

    deployment_uid: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    config: FinalInferenceDeploymentConfig
    created_by: str
    public_dns: str = ""

    deleted_at: Optional[datetime] = None
    submitted_config: Optional[InferenceDeploymentConfig] = None

    _required_properties: Tuple[str] = tuple(
        ['id', 'name', 'status', 'createdAt', 'updatedAt', 'inferenceDeploymentInput', 'publicDNS'])

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]):
        missing = set(cls._required_properties) - set(response)
        if missing:
            raise MAPIException(
                status=HTTPStatus.BAD_REQUEST,
                message=f'Missing required key(s) in response to deserialize Deployment object: {", ".join(missing)}',
            )

        deleted_at = None
        if response['deletedAt'] is not None:
            deleted_at = convert_datetime(response['deletedAt'])

        submit_config = None
        if response.get('originalInferenceDeploymentInput', {}):
            submit_config = InferenceDeploymentConfig.from_mapi_response(response['originalInferenceDeploymentInput'])

        return cls(deployment_uid=response['id'],
                   name=response['name'],
                   created_at=convert_datetime(response['createdAt']),
                   updated_at=convert_datetime(response['updatedAt']),
                   deleted_at=deleted_at,
                   status=response['status'],
                   public_dns=response['publicDNS'],
                   created_by=response['createdByEmail'],
                   config=FinalInferenceDeploymentConfig.from_mapi_response(response['inferenceDeploymentInput']),
                   submitted_config=submit_config)
