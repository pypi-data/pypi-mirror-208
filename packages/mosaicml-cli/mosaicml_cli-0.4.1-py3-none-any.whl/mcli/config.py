"""Global Singleton Config Store"""
from __future__ import annotations

import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import ruamel.yaml
import yaml
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from mcli.api.exceptions import MCLIConfigError
from mcli.models import Cluster
from mcli.utils.utils_serializable_dataclass import SerializableDataclass
from mcli.utils.utils_yaml import StringDumpYAML

logger = logging.getLogger(__name__)


def env_path_override_config(config_value: str):
    if config_value in os.environ:
        globals()[config_value] = Path(os.environ[config_value])


def env_str_override_config(config_value: str):
    if config_value in os.environ:
        globals()[config_value] = os.environ[config_value]


MCLI_CONFIG_DIR: Path = Path(os.path.expanduser('~/.mosaic'))
env_path_override_config('MCLI_CONFIG_DIR')

MCLI_BACKUP_CONFIG_DIR: Path = Path(os.path.expanduser('~/.mosaic.bak'))
env_path_override_config('MCLI_BACKUP_CONFIG_DIR')

MOSAICML_API_ENDPOINT: str = 'https://api.mosaicml.com/graphql'
MOSAICML_API_ENDPOINT_STAGING: str = 'https://staging.api.mosaicml.com/graphql'
MOSAICML_API_ENDPOINT_DEV: str = 'https://dev.api.mosaicml.com/graphql'
MOSAICML_API_ENDPOINT_LOCAL: str = 'http://localhost:3001/graphql'
MOSAICML_API_ENDPOINT_ENV: str = 'MOSAICML_API_ENDPOINT'
env_str_override_config(MOSAICML_API_ENDPOINT_ENV)

MOSAICML_MINT_ENDPOINT: str = 'wss://mint.mosaicml.com/v1/shell'
MOSAICML_MINT_ENDPOINT_STAGING: str = 'wss://staging.mint.mosaicml.com/v1/shell'
MOSAICML_MINT_ENDPOINT_DEV: str = 'wss://dev.mint.mosaicml.com/v1/shell'
MOSAICML_MINT_ENDPOINT_LOCAL: str = 'ws://localhost:3004/v1/shell'
MOSAICML_MINT_ENDPOINT_ENV: str = 'MOSAICML_MINT_ENDPOINT'
env_str_override_config(MOSAICML_MINT_ENDPOINT_ENV)

MCLI_CONFIG_PATH: Path = MCLI_CONFIG_DIR / 'mcli_config'
env_path_override_config('MCLI_CONFIG_PATH')

MCLI_KUBECONFIG: Path = MCLI_CONFIG_DIR / 'kube_config'
env_path_override_config('MCLI_KUBECONFIG')

UPDATE_CHECK_FREQUENCY_DAYS: float = 2

MCLI_MODE_ENV: str = 'MCLI_MODE'
env_str_override_config(MCLI_MODE_ENV)

MCLI_INTERACTIVE_ENV: str = 'MCLI_INTERACTIVE'
env_str_override_config(MCLI_INTERACTIVE_ENV)

MCLI_TIMEOUT_ENV = 'MCLI_TIMEOUT'
env_str_override_config(MCLI_TIMEOUT_ENV)

MCLI_DISABLE_UPGRADE_CHECK_ENV: str = 'MCLI_DISABLE_UPGRADE_CHECK'
env_str_override_config(MCLI_DISABLE_UPGRADE_CHECK_ENV)

# Used for local dev and testing
MOSAICML_API_KEY_ENV: str = 'MOSAICML_API_KEY'

logging.getLogger('urllib3.connectionpool').disabled = True

logger = logging.getLogger(__name__)

ADMIN_MODE = False


def get_timeout(default_timeout: Optional[float] = None) -> Optional[float]:
    timeout_env = os.environ.get(MCLI_TIMEOUT_ENV)

    if timeout_env:
        return float(timeout_env)

    return default_timeout


class FeatureFlag(Enum):
    """Enum for mcli feature flags
    """
    ALPHA_TESTER = 'ALPHA_TESTER'
    MCLOUD_INTERACTIVE = 'MCLOUD_INTERACTIVE'

    @staticmethod
    def get_external_features() -> Set[FeatureFlag]:
        return set()


class MCLIMode(Enum):
    """Enum for mcli user modes
    """
    PROD = 'PROD'
    DEV = 'DEV'
    INTERNAL = 'INTERNAL'
    LOCAL = 'LOCAL'
    LEGACY = 'LEGACY'
    STAGING = 'STAGING'

    def is_legacy(self) -> bool:
        """True if this mode is a legacy mode
        """
        return self == MCLIMode.LEGACY

    def is_internal(self) -> bool:
        """True if this mode is an internal mode
        """
        internal_modes = {MCLIMode.DEV, MCLIMode.INTERNAL, MCLIMode.LOCAL, MCLIMode.STAGING}
        return self in internal_modes

    def available_feature_flags(self) -> List[FeatureFlag]:
        if self.is_internal():
            # All features are available to internal users
            return list(FeatureFlag)

        return list(FeatureFlag.get_external_features())

    @classmethod
    def from_env(cls) -> MCLIMode:
        """If the user's mcli mode is set in the environment, return it
        """
        found_mode = os.environ.get(MCLI_MODE_ENV, None)
        if found_mode:
            found_mode = found_mode.upper()
            for mode in MCLIMode:
                if found_mode == mode.value:
                    return mode

        if os.environ.get('DOGEMODE', None) == 'ON':
            return MCLIMode.INTERNAL

        return MCLIMode.PROD

    @property
    def endpoint(self) -> str:
        """The MAPI endpoint value for the given environment
        """
        if self is MCLIMode.DEV:
            return MOSAICML_API_ENDPOINT_DEV
        elif self is MCLIMode.LOCAL:
            return MOSAICML_API_ENDPOINT_LOCAL
        elif self is MCLIMode.STAGING:
            return MOSAICML_API_ENDPOINT_STAGING
        return MOSAICML_API_ENDPOINT

    @property
    def mint_endpoint(self) -> str:
        """The MINT endpoint value for the given environment
        """
        if self is MCLIMode.DEV:
            return MOSAICML_MINT_ENDPOINT_DEV
        elif self is MCLIMode.LOCAL:
            return MOSAICML_MINT_ENDPOINT_LOCAL
        elif self is MCLIMode.STAGING:
            return MOSAICML_MINT_ENDPOINT_STAGING
        return MOSAICML_MINT_ENDPOINT

    def is_alternate(self) -> bool:
        """True if the mode is a valid alternate mcloud environment
        """
        alternate_env_modes = {MCLIMode.DEV, MCLIMode.LOCAL, MCLIMode.STAGING}
        return self in alternate_env_modes


@dataclass
class MCLIConfig(SerializableDataclass):
    """Global Config Store persisted on local disk"""

    # set to default for now to not break existing users' configs
    MOSAICML_API_KEY: str = ''  # pylint: disable=invalid-name Global Stored within Singleton

    feature_flags: Dict[str, bool] = field(default_factory=dict)
    last_update_check: datetime = field(default_factory=datetime.now)

    # Registered Clusters
    clusters: List[Cluster] = field(default_factory=list)

    # MCloud environments w/ API keys
    # Most users will be in PROD, so this will likely only be touched internally
    mcloud_envs: Dict[str, str] = field(default_factory=dict)

    _user_id: Optional[str] = None

    @property
    def user_id(self):
        # User id is only relevant in admin mode. If using normal mcli, it should always
        # set to be blank and the user just needs to authenticate through their api key
        if ADMIN_MODE:
            return self._user_id
        return None

    @user_id.setter
    def user_id(self, value: Optional[str]):
        self._user_id = value

    @classmethod
    def empty(cls) -> MCLIConfig:
        conf = MCLIConfig()
        return conf

    @property
    def internal(self) -> bool:
        return self.mcli_mode.is_internal()

    @property
    def mcli_mode(self) -> MCLIMode:
        return MCLIMode.from_env()

    @property
    def allow_interactive(self) -> bool:
        interactive_env = os.environ.get(MCLI_INTERACTIVE_ENV, 'false').lower()
        return interactive_env == 'true' or self.internal

    @property
    def disable_upgrade(self) -> bool:
        disable_env = os.environ.get(MCLI_DISABLE_UPGRADE_CHECK_ENV, 'false').lower()
        return disable_env == 'true'

    @property
    def endpoint(self) -> str:
        """The user's MAPI endpoint
        """
        env_endpoint = os.environ.get(MOSAICML_API_ENDPOINT_ENV, None)

        return env_endpoint or self.mcli_mode.endpoint

    @property
    def mint_endpoint(self) -> str:
        """The user's MINT endpoint
        """
        env_endpoint = os.environ.get(MOSAICML_MINT_ENDPOINT_ENV, None)

        return env_endpoint or self.mcli_mode.mint_endpoint

    @property
    def api_key(self):
        """The user's configured MCloud API key
        """
        return self.get_api_key(env_override=True)

    @api_key.setter
    def api_key(self, value: str):
        if self.mcli_mode.is_alternate():
            # If the user is using an alternative mcloud, set that API key
            self.mcloud_envs[self.mcli_mode.value] = value
        else:
            self.MOSAICML_API_KEY = value

    def get_api_key(self, env_override: bool = True):
        """Get the user's current API key

        Args:
            env_override (bool, optional): If True, allow an environment variable to
                override the configured value, otherwise pull only from the user's config
                file. Defaults to True.

        Returns:
            str: The user's API key, if set, otherwise an empty string
        """
        api_key_env = os.environ.get(MOSAICML_API_KEY_ENV, None)
        if api_key_env is not None and env_override:
            return api_key_env
        elif self.mcli_mode.is_alternate():
            return self.mcloud_envs.get(self.mcli_mode.value, '')
        elif self.MOSAICML_API_KEY:
            return self.MOSAICML_API_KEY
        return ''

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MCLIConfig:
        # TODO: Remove after full deprecation transition
        if 'dev_mode' in data:
            del data['dev_mode']
        if 'internal' in data:
            del data['internal']
        # TODO(END): Remove after full deprecation transition

        # Backwards compatibility: platforms should be synonymous with clusters
        if 'platforms' in data:
            data['clusters'] = data['platforms']
            del data['platforms']

        if 'environment_variables' in data:
            del data['environment_variables']

        data['clusters'] = []

        # Remove any unknown feature flags
        known_feature_flags = {f.value for f in FeatureFlag}
        data['feature_flags'] = {k: v for k, v in data.get('feature_flags', {}).items() if k in known_feature_flags}

        return super().from_dict(data)

    @classmethod
    def load_config(cls, safe: bool = False) -> MCLIConfig:
        """Loads the MCLIConfig from local disk


        Args:
            safe (bool): If safe is true, if the config fails to load it will return
                an empty generated config

        Return:
            Returns the MCLIConfig if successful, otherwise raises MCLIConfigError
        """
        try:
            with open(MCLI_CONFIG_PATH, 'r', encoding='utf8') as f:
                data: Dict[str, Any] = yaml.full_load(f)
            conf: MCLIConfig = cls.from_dict(data)
        except FileNotFoundError as e:
            if safe:
                return MCLIConfig.empty()
            raise MCLIConfigError(Messages.MCLI_NOT_INITIALIZED) from e

        # Optional values can get filled in over time. If a new optional value is not
        # present in the config, let it be filled in by the default, if one was set.
        if set(asdict(conf)) != set(data):
            # TODO: Bug on over-saving HEK-452
            conf.save_config()  # pylint: disable=no-member

        return conf

    def save_config(self) -> bool:
        """Saves the MCLIConfig to local disk

        Return:
            Returns true if successful
        """
        data = self._get_formatted_dump()
        y = YAML()
        y.explicit_start = True  # type: ignore
        with open(MCLI_CONFIG_PATH, 'w', encoding='utf8') as f:
            y.dump(data, f)
        return True

    def _get_formatted_dump(self) -> CommentedMap:
        """Gets the ruamel yaml formatted dump of the config
        """
        raw_data = self.to_disk()

        # Remove clusters
        del raw_data['clusters']

        data: CommentedMap = ruamel.yaml.load(
            yaml.dump(raw_data),
            ruamel.yaml.RoundTripLoader,
        )
        return data

    def feature_enabled(self, feature: FeatureFlag) -> bool:
        """Checks if the feature flag is enabled

        Args:
            feature (FeatureFlag): The feature to check
        """

        if not self.internal and feature not in FeatureFlag.get_external_features():
            # Only enable select features for external use
            return False

        if feature.value in self.feature_flags:
            enabled = self.feature_flags.get(feature.value, False)
            return bool(enabled)

        return False

    def __str__(self) -> str:
        data = self._get_formatted_dump()
        y = StringDumpYAML()
        return y.dump(data)


def feature_enabled(feature: FeatureFlag) -> bool:
    conf = MCLIConfig.load_config(safe=True)
    return conf.feature_enabled(feature=feature)


class Messages():
    MCLI_NOT_INITIALIZED = 'MCLI not yet initialized. Please run `mcli init` first.'
    API_KEY_MISSING = 'No API key found. Please create one and set it using `mcli set api-key`.'


MESSAGE = Messages()
