import os
from contextlib import contextmanager

import pytest

from mcli.config import (MCLI_INTERACTIVE_ENV, MCLI_MODE_ENV, MOSAICML_API_ENDPOINT, MOSAICML_API_ENDPOINT_DEV,
                         MOSAICML_API_ENDPOINT_ENV, MOSAICML_API_ENDPOINT_LOCAL, MOSAICML_API_KEY_ENV, FeatureFlag,
                         MCLIConfig, MCLIConfigError, MCLIMode)


@contextmanager
def clear_envs(*envs):
    values = {}
    for k in envs:
        values[k] = os.environ.pop(k, None)
    yield
    for k, v in values.items():
        if v is not None:
            os.environ[k] = v


@pytest.mark.parametrize("cluster_key", ["clusters", "platforms"])
def test_backwards_compatible_mcli_config(cluster_key, mocker):
    """MCLIConfig should be able to load backwards compatible mcli configs
    """
    mocker.patch('mcli.config.MCLIConfig.internal', new_callable=mocker.PropertyMock, return_value=True)
    data = {
        'feature_flags': {
            'UNKNOWN_FLAG_SHOULDNT_BREAK_THINGS': True,
            'ALPHA_TESTER': True
        },
        cluster_key: [
            {
                'kubernetes_context': 'microk8s',
                'name': 'microk8s',
                'namespace': 'microk8s',
            },
            # these should be ignored
            {
                'kubernetes_context': 'unknown',
                'name': 'unknown',
                'namespace': 'unknown',
            },
            {
                'kubernetes_context': 'aws-research-01',
            },
        ],
        # these should be removed
        'dev_mode': True,
        'internal': True,
    }
    mcli_config = MCLIConfig.from_dict(data)
    assert mcli_config.feature_flags
    assert mcli_config.feature_enabled(FeatureFlag.ALPHA_TESTER)


def test_uninitialized(new_mcli_setup):
    """Test MCLIConfig fails to load for a new setup, raising a custom exception
    """
    with pytest.raises(MCLIConfigError):
        MCLIConfig.load_config()


def test_initialized(base_mcli_setup):
    """Test MCLIConfig successfully loads
    """
    config = MCLIConfig.load_config()

    # defaults
    assert not config.internal
    assert config.mcli_mode == MCLIMode.PROD
    assert config.endpoint == MOSAICML_API_ENDPOINT


def test_config_save_load(new_mcli_setup):
    """Test basic save and load
    """
    conf = MCLIConfig.empty()
    conf.save_config()

    conf2 = MCLIConfig.load_config()
    assert conf.to_dict() == conf2.to_dict()


def test_mcli_mode(new_mcli_setup):
    with clear_envs(MCLI_MODE_ENV, 'DOGEMODE'):
        conf = MCLIConfig.empty()
        assert conf.mcli_mode == MCLIMode.PROD

        os.environ[MCLI_MODE_ENV] = MCLIMode.DEV.value
        assert conf.mcli_mode == MCLIMode.DEV

        os.environ[MCLI_MODE_ENV] = MCLIMode.INTERNAL.value
        assert conf.mcli_mode == MCLIMode.INTERNAL

        os.environ[MCLI_MODE_ENV] = MCLIMode.LOCAL.value
        assert conf.mcli_mode == MCLIMode.LOCAL

        os.environ[MCLI_MODE_ENV] = 'UNKNOWN'
        assert conf.mcli_mode == MCLIMode.PROD

        del os.environ[MCLI_MODE_ENV]
        os.environ['DOGEMODE'] = 'ON'
        assert conf.mcli_mode == MCLIMode.INTERNAL

        os.environ['DOGEMODE'] = 'UNKNOWN'
        assert conf.mcli_mode == MCLIMode.PROD


def test_api_endpoint(new_mcli_setup):
    with clear_envs(MOSAICML_API_ENDPOINT_ENV, MCLI_MODE_ENV):
        conf = MCLIConfig.empty()
        assert conf.endpoint == MOSAICML_API_ENDPOINT

        os.environ[MCLI_MODE_ENV] = MCLIMode.INTERNAL.value
        assert conf.endpoint == MOSAICML_API_ENDPOINT

        os.environ[MCLI_MODE_ENV] = MCLIMode.DEV.value
        assert conf.endpoint == MOSAICML_API_ENDPOINT_DEV

        os.environ[MCLI_MODE_ENV] = MCLIMode.LOCAL.value
        assert conf.endpoint == MOSAICML_API_ENDPOINT_LOCAL

        os.environ[MCLI_MODE_ENV] = 'UNKNOWN'
        assert conf.endpoint == MOSAICML_API_ENDPOINT

        env_endpoint = 'https://some-endpoint.com/graphql'
        os.environ[MOSAICML_API_ENDPOINT_ENV] = 'https://some-endpoint.com/graphql'
        assert conf.endpoint == env_endpoint


def test_api_key_set(new_mcli_setup):
    with clear_envs(MOSAICML_API_KEY_ENV, MCLI_MODE_ENV):
        conf = MCLIConfig.empty()
        assert conf.api_key == ''

        # Prod API key is stored as the global API key
        prod_api_key = 'some-prod-api-key'
        conf.api_key = prod_api_key
        assert conf.api_key == prod_api_key
        assert conf.MOSAICML_API_KEY == prod_api_key

        # Dev API key is stored in mcloud_envs - keep it separate
        dev_api_key = 'some-dev-api-key'
        os.environ[MCLI_MODE_ENV] = MCLIMode.DEV.value
        conf.api_key = dev_api_key
        assert conf.api_key == dev_api_key
        assert conf.mcloud_envs['DEV'] == dev_api_key
        assert conf.MOSAICML_API_KEY == prod_api_key

        # Local API key is stored in mcloud_envs - keep it separate
        local_api_key = 'some-local-api-key'
        os.environ[MCLI_MODE_ENV] = MCLIMode.LOCAL.value
        conf.api_key = local_api_key
        assert conf.api_key == local_api_key
        assert conf.mcloud_envs[MCLIMode.LOCAL.value] == local_api_key
        assert conf.MOSAICML_API_KEY == prod_api_key

        # Also env override
        env_api_key = 'some-env-api-key'
        os.environ[MOSAICML_API_KEY_ENV] = env_api_key
        assert conf.api_key == env_api_key


def test_interactive_enabled(new_mcli_setup):
    with clear_envs(MCLI_INTERACTIVE_ENV, MCLI_MODE_ENV):
        conf = MCLIConfig.empty()
        assert conf.allow_interactive is False

        for value in ('true', 'TRUE'):
            os.environ[MCLI_INTERACTIVE_ENV] = value
            assert conf.allow_interactive is True

        for value in ('false', 'unknown'):
            os.environ[MCLI_INTERACTIVE_ENV] = value
            assert conf.allow_interactive is False

        del os.environ[MCLI_INTERACTIVE_ENV]

        os.environ[MCLI_MODE_ENV] = MCLIMode.INTERNAL.value
        assert conf.allow_interactive is True
