""" Deployment Input """
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from http import HTTPStatus
from typing import Any, Dict, List, Optional

import yaml
from typing_extensions import TypedDict

from mcli.api.exceptions import MAPIException, MCLIDeploymentConfigValidationError
from mcli.api.schema.generic_model import DeserializableModel
from mcli.models.run_config import _clean_run_name
from mcli.utils.utils_config import (BaseSubmissionConfig, EnvVarTranslation, IntegrationTranslation, Translation,
                                     uuid_generator)
from mcli.utils.utils_string_functions import validate_image

logger = logging.getLogger(__name__)

DEPLOYMENT_CONFIG_UID_LENGTH = 6


class ModelConfig(TypedDict, total=False):
    """Typed dictionary for model configs"""
    downloader: str
    download_parameters: Dict[str, str]
    model_handler: str
    model_parameters: Dict[str, str]


@dataclass
class FinalInferenceDeploymentConfig(DeserializableModel):
    """A finalized deployment configuration
    This configuration must be complete, with enough details to submit a new deployment to the
    MosaicML Cloud.
    """

    deployment_id: str
    name: str
    gpu_num: int
    image: str
    replicas: int
    env_variables: List[Dict[str, str]]
    integrations: List[Dict[str, Any]]

    metadata: Dict[str, Any] = field(default_factory=dict)

    # Model config - optional for backwards-compatibility
    model: ModelConfig = field(default_factory=ModelConfig)

    gpu_type: str = ''
    command: str = ''

    cluster: str = ''

    _property_translations = {
        'deployment_id': 'deployment_id',
        'deploymentName': 'name',
        'gpuType': 'gpu_type',
        'gpuNum': 'gpu_num',
        'cluster': 'cluster',
        'image': 'image',
        'command': 'command',
        'replicas': 'replicas',
        'metadata': 'metadata',
        'envVariables': 'env_variables',
        'integrations': 'integrations',
        'model': 'model',
    }

    def __str__(self) -> str:
        return yaml.safe_dump(asdict(self))

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> FinalInferenceDeploymentConfig:

        # Backwards Compatability
        if 'metadata' not in response:
            response['metadata'] = {}

        if 'envVariables' not in response:
            response['envVariables'] = []

        if 'integrations' not in response:
            response['integrations'] = []

        if 'model' not in response:
            response['model'] = {
                'checkpointPath': '',
            }

        missing = set(cls._property_translations) - set(response)
        if missing:
            raise MAPIException(
                status=HTTPStatus.BAD_REQUEST,
                message=('Missing required key(s) in response to deserialize '
                         f'FinalDeploymentConfig object: {", ".join(missing)}'),
            )
        data = {}
        for k, v in cls._property_translations.items():
            value = response[k]
            if v == 'env_variables':
                value = EnvVarTranslation.from_mapi(value)
            elif v == 'integrations':
                value = IntegrationTranslation.from_mapi(value)
            elif v == 'model':
                value = InferenceModelTranslation.from_mapi(value)
            data[v] = value

        return cls(**data)

    @classmethod
    def finalize_config(cls, deployment_config: InferenceDeploymentConfig) -> FinalInferenceDeploymentConfig:
        """Create a :class:`~mcli.models.deployment_config.FinalDeploymentConfig` from the provided
        :class:`~mcli.models.deployment_config.DeploymentConfig`.
        If the :class:`~mcli.models.deployment_config.DeploymentConfig` is not fully populated then
        this function fails with an error.
        Args:
            deployment_config (:class:`~mcli.models.deployment_config.DeploymentConfig`): The DeploymentConfig
            to finalize
        Returns:
            :class:`~mcli.models.deployment_config.FinalDeploymentConfig`:The object created using values from the input
        Raises:
            :class:`~mcli.api.exceptions.MCLIConfigError`: If MCLI config is not present or is missing information
            :class:`~mcli.api.exceptions.MCLIDeploymentConfigValidationError`: If deployment_config is not valid
        """

        model_as_dict = asdict(deployment_config)

        missing_fields = [field for field, value in model_as_dict.items() if value is None]
        for missing in missing_fields:
            model_as_dict.pop(missing, None)

        # required for FinalDeploymentConfig, even though not required for mcloud
        if not model_as_dict.get("gpu_num"):
            model_as_dict["gpu_num"] = 0

        if not model_as_dict.get("replicas"):
            model_as_dict["replicas"] = 1

        if not model_as_dict.get("metadata"):
            model_as_dict["metadata"] = {}

        # Fill in default initial values for FinalDeploymentConfig
        model_as_dict.update({
            'deployment_id': uuid_generator(DEPLOYMENT_CONFIG_UID_LENGTH),
        })
        model_as_dict['name'] = _clean_run_name(model_as_dict.get('name'))

        if isinstance(model_as_dict.get('gpu_type'), int):
            model_as_dict['gpu_type'] = str(model_as_dict['gpu_type'])

        image = model_as_dict.get('image')
        if not image:
            raise MCLIDeploymentConfigValidationError('An image name must be provided using the keyword [bold]image[/]')
        elif not validate_image(image):
            raise MCLIDeploymentConfigValidationError(f'The image name "{model_as_dict["image"]}" is not valid')

        return cls(**model_as_dict)

    def to_create_deployment_api_input(self) -> Dict[str, Dict[str, Any]]:
        """Convert a deployment configuration to a proper JSON to pass to MAPI's createDeployment
        Returns:
            Dict[str, Dict[str, Any]]: The deployment configuration as a MAPI deploymentInput JSON
        """
        translations = {v: k for k, v in self._property_translations.items()}

        translated_input = {}
        for field_name, value in asdict(self).items():
            translated_name = translations.get(field_name, field_name)
            if field_name == 'env_variables':
                value = EnvVarTranslation.to_mapi(value)
            elif field_name == 'integrations':
                value = IntegrationTranslation.to_mapi(value)
            elif field_name == 'model':
                value = InferenceModelTranslation.to_mapi(value)
            elif field_name == "gpu_type" and not value:
                continue
            elif field_name == "cluster" and not value:
                continue
            translated_input[translated_name] = value
        return {
            'inferenceDeploymentInput': translated_input,
        }


@dataclass
class InferenceDeploymentConfig(BaseSubmissionConfig):
    """A deployment configuration for the MosaicML Cloud

    Values in here are not yet validated and some required values may be missing.
    
    Args:
        name (`Optional[str]`): User-defined name of the deployment
        gpu_type (`Optional[str]`): GPU type (optional if only one gpu type for your cluster)
        gpu_num (`Optional[int]`): Number of GPUs
        cluster (`Optional[str]`): Cluster to use (optional if you only have one)
        image (`Optional[str]`): Docker image (e.g. `mosaicml/composer`)
        command (`str`): Command to use when a deployment starts
        replicas (`Optional[int]`): Number of replicas to create
        env_variables (`List[Dict[str, str]]`): List of environment variables
        integrations (`List[Dict[str, Any]]`): List of integrations
    """
    name: Optional[str] = None
    gpu_type: Optional[str] = None
    gpu_num: Optional[int] = None
    cluster: Optional[str] = None
    image: Optional[str] = None
    replicas: Optional[int] = None
    command: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    env_variables: List[Dict[str, str]] = field(default_factory=list)
    integrations: List[Dict[str, Any]] = field(default_factory=list)
    model: ModelConfig = field(default_factory=ModelConfig)

    _property_translations = {
        'deploymentName': 'name',
        'gpuNum': 'gpu_num',
        'cluster': 'cluster',
        'image': 'image',
        'command': 'command',
        'replicas': 'replicas',
        'metadata': 'metadata',
        'envVariables': 'env_variables',
        'integrations': 'integrations',
        'model': 'model',
    }

    _required_display_properties = {'name', 'image', 'command', 'replicas'}

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> InferenceDeploymentConfig:
        data = {}
        for k, v in cls._property_translations.items():
            if k not in response:
                # This must be an optional property, so skip
                continue
            value = response[k]
            if v == 'env_variables':
                value = EnvVarTranslation.from_mapi(value)
            elif v == 'integrations':
                value = IntegrationTranslation.from_mapi(value)
            elif v == 'model':
                value = InferenceModelTranslation.from_mapi(value)
            data[v] = value

        return cls(**data)


class InferenceModelTranslation(Translation[ModelConfig, Dict[str, Any]]):
    """Translate model configs to and from MAPI"""

    _property_translations = {
        'downloader': 'downloader',
        'download_parameters': 'downloadParameters',
        'model_handler': 'modelHandler',
        'model_parameters': 'modelParameters',
    }

    @classmethod
    def from_mapi(cls, value: Dict[str, Any]) -> ModelConfig:
        translated_config = {}
        for mcli_key, mapi_key in cls._property_translations.items():
            translated_config[mcli_key] = value.get(mapi_key)

        return ModelConfig(**translated_config)

    @classmethod
    def to_mapi(cls, value: ModelConfig) -> Dict[str, Any]:
        translated_config = {}
        for mcli_key, val in value.items():
            mapi_key = cls._property_translations.get(mcli_key)
            translated_config[mapi_key] = val

        return translated_config
