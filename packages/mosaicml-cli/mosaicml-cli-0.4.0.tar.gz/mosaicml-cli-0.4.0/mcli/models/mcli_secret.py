""" MCLI Abstraction for Secrets """
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Type, TypeVar

import yaml

from mcli.api.exceptions import MAPI_DESERIALIZATION_ERROR
from mcli.api.schema.generic_model import DeserializableModel
from mcli.utils.utils_serializable_dataclass import SerializableDataclass, T_SerializableDataclass
from mcli.utils.utils_types import CommonEnum

SECRET_MOUNT_PATH_PARENT = Path('/secrets')
EnumType = TypeVar('EnumType', bound=Enum)  # pylint: disable=invalid-name

MAPI_TO_MCLI_SECRET_TYPE = {
    'MOUNTED': 'mounted',
    'ENV_VAR': 'environment',
    'DOCKER_REGISTRY': 'docker_registry',
    'S3': 's3',
    'SSH': 'ssh',
    'GIT_SSH': 'git',
    'SFTP_SSH': 'sftp',
    'GCP': 'gcp',
    'OCI': 'oci'
}


def get_mapi_secret_type(val: SecretType) -> str:
    for mapi_secret_type, mcli_secret_type in MAPI_TO_MCLI_SECRET_TYPE.items():
        if val.value == mcli_secret_type:
            return mapi_secret_type
    raise KeyError(f'Unknown secret type {val.value}')


class SecretType(CommonEnum):
    """ Enum for Types of Secrets Allowed """

    docker_registry = 'docker_registry'
    environment = 'environment'
    generic = 'generic'
    git = 'git'
    mounted = 'mounted'
    sftp = 'sftp'
    ssh = 'ssh'
    s3 = 's3'
    gcp = 'gcp'
    oci = 'oci'

    @classmethod
    def ensure_enum(cls, val):
        if isinstance(val, cls):
            return val

        if not isinstance(val, str):
            raise ValueError(f'Unable to ensure {val} is a {cls.__name__} enum')

        try:
            return SecretType[val]
        except KeyError:
            pass

        backwards_compatible_secrets = {
            's3_credentials': SecretType.s3,
        }

        try:
            return backwards_compatible_secrets[val]
        except KeyError as e:
            raise ValueError(f'Unknown secret type {val}') from e


def secret_type_to_class(secret_type: SecretType) -> Type[Secret]:
    """Maps the secret type to Secret subclass"""
    # pylint: disable-next=import-outside-toplevel
    from mcli.objects.secrets import SECRET_CLASS_MAP

    try:
        return SECRET_CLASS_MAP[secret_type]
    except KeyError as e:
        raise NotImplementedError(f'Secret of type: { secret_type } not supported yet') from e


@dataclass
class Secret(SerializableDataclass, DeserializableModel, ABC):
    """
    The Base Secret Class for MCLI Secrets

    Secrets can not nest other SerializableDataclass objects
    """

    name: str
    secret_type: SecretType
    created_at: Optional[datetime] = None
    id: Optional[str] = None

    def __str__(self):
        return f'{self.name} ({self.secret_type})'

    def __lt__(self, other: Secret):
        if not isinstance(other, Secret):
            raise TypeError(f'Cannot compare order of ``Secret`` and {type(other)}')
        return self.name > other.name

    def __gt__(self, other: Secret):
        if not isinstance(other, Secret):
            raise TypeError(f'Cannot compare order of ``Secret`` and {type(other)}')
        return self.name < other.name

    def __le__(self, other: Secret):
        if not isinstance(other, Secret):
            raise TypeError(f'Cannot compare order of ``Secret`` and {type(other)}')
        return self.name >= other.name

    def __ge__(self, other: Secret):
        if not isinstance(other, Secret):
            raise TypeError(f'Cannot compare order of ``Secret`` and {type(other)}')
        return self.name <= other.name

    @property
    def mapi_data(self) -> Dict[str, Any]:
        """Data used to create the secret in MAPI
        """
        raise NotImplementedError

    @classmethod
    def from_dict(cls: Type[T_SerializableDataclass], data: Dict[str, Any]) -> Secret:
        if not isinstance(data, dict):
            raise TypeError(f'Secret data must be structured as a dictionary. Got: {type(data)}')

        secret_type_string = data.pop('secret_type', None)
        if not secret_type_string:
            raise ValueError(f'No `secret_type` found for secret with data: \n{yaml.dump(data)}')

        secret_type = SecretType.ensure_enum(secret_type_string)
        assert isinstance(secret_type, SecretType)

        secret = secret_type_to_class(secret_type)(secret_type=secret_type, **data)
        assert isinstance(secret, Secret)
        return secret  # type: ignore

    @staticmethod
    def _mapi_required_properties() -> Tuple[str]:
        """Required properties for mapi response"""
        return tuple(['name', 'type', 'metadata'])

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> Secret:
        required_properties = set(cls._mapi_required_properties())
        missing = required_properties - set(response)
        if missing:
            raise MAPI_DESERIALIZATION_ERROR

        try:
            secret_type = SecretType[MAPI_TO_MCLI_SECRET_TYPE[response['type']]]
            secret_type_cls = secret_type_to_class(secret_type)

            try:
                created_at = datetime.strptime(response['createdAt'], "%Y-%m-%dT%H:%M:%S.%f%z")
            except (TypeError, ValueError):
                created_at = None

            secret_id = response.get('id')
            secret = secret_type_cls(
                name=response['name'],
                secret_type=secret_type,
                created_at=created_at,
                id=secret_id,
            )

            if secret_type in {SecretType.mounted, SecretType.ssh, SecretType.git, SecretType.gcp}:
                setattr(secret, 'mount_path', response['metadata']['mountPath'])
            elif secret_type == SecretType.environment:
                setattr(secret, 'key', response['metadata']['key'])
            elif secret_type in {SecretType.s3}:
                setattr(secret, 'mount_directory', response['metadata']['mountDirectory'])
                setattr(secret, 'credentials', response.get('value', {}).get('credentials'))
                setattr(secret, 'config', response.get('value', {}).get('config'))
            elif secret_type in {SecretType.oci}:
                setattr(secret, 'mount_directory', response['metadata']['mountDirectory'])
                setattr(secret, 'key_file', response.get('value', {}).get('keyFile'))
                setattr(secret, 'config', response.get('value', {}).get('config'))
            return secret
        except KeyError as e:
            raise MAPI_DESERIALIZATION_ERROR from e


@dataclass
class MCLIGenericSecret(Secret):
    """Secret class for generic secrets
    """
    value: Optional[str] = None
