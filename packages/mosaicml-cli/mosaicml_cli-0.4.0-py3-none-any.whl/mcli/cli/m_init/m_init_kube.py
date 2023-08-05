""" mcli init_kube Entrypoint """
import argparse
import json
import logging
import re
import webbrowser
from typing import Dict, List, NamedTuple, Optional

import requests
import yaml

from mcli.api.exceptions import MCLIException
from mcli.config import MCLI_CONFIG_DIR, MCLI_KUBECONFIG
from mcli.utils.utils_interactive import secret_prompt, simple_prompt
from mcli.utils.utils_logging import FAIL, OK
from mcli.utils.utils_spinner import console_status
from mcli.utils.utils_string_functions import validate_rfc1123_name

RANCHER_ENDPOINT_PATTERN = 'https://rancher.z[0-9]+.r[0-9]+.mosaicml.cloud'
DEEP_LINKS = {
    'DEFAULT': 'dashboard/account/create-key',
    'https://mosaicml-rancher.westus2.cloudapp.azure.com': 'apikeys'
}

logger = logging.getLogger(__name__)


class ValidationError(MCLIException):
    """Base class for interactive validation errors
    """


def bold(text: str) -> str:
    return f'[bold green]{text}[/]'


def validate_rancher_endpoint(endpoint: str) -> bool:
    if re.match(RANCHER_ENDPOINT_PATTERN.replace('.', r'\.'), endpoint):
        return True
    raise RuntimeError(f'Invalid MosaicML platform endpoint: {endpoint}. Should be of the form: '
                       f'{RANCHER_ENDPOINT_PATTERN}')


class RancherDetails(NamedTuple):
    endpoint: str
    auth_token: str
    namespace: str


def validate_auth_token(text: str) -> bool:
    if not text.startswith('token'):
        raise ValidationError('Bearer token should start with "token"')
    return True


def validate_number(text: str) -> bool:
    if not text.isnumeric():
        raise ValidationError(f'Zone must be a number. Got: {text}')
    return True


def fill_rancher_values(
    auth_token: Optional[str] = None,
    rancher_endpoint: Optional[str] = None,
    namespace: Optional[str] = None,
) -> RancherDetails:
    if not rancher_endpoint:
        zone = simple_prompt(
            'Which MosaicML platform "zone" would you like to access?',
            validate=validate_number,
        )
        rancher_endpoint = f'https://rancher.z{zone}.r0.mosaicml.cloud'

    assert rancher_endpoint is not None

    # Get required info
    if not auth_token:
        path = DEEP_LINKS.get(rancher_endpoint, None) or DEEP_LINKS['DEFAULT']
        url = f'{rancher_endpoint}/{path}'
        logger.info(
            '\n\nTo communicate with the MosaicML platform we\'ll need your API key '
            f'(also called the "{bold("Bearer Token")}"). '
            'Your browser should have opened to the API key creation screen. Login, if necessary, then, create a '
            f'key with "{bold("no scope")}" that expires "{bold("A day from now")}" and copy the '
            f'"{bold("Bearer Token")}" for this next step. If your browser did not open, please use this link:'
            f'\n\n[blue]{url}[/]\n\n'
            'If upon login you do not see the API key creation screen, either try the link above in Google Chrome or '
            f'select "{bold("Accounts & API Keys")}" from the top-right user menu, followed by '
            f'"{bold("Create API Key")}" and the directions above.')
        webbrowser.open_new_tab(url)

        auth_token = secret_prompt('What is your "bearer token"?', validate=validate_auth_token)

    assert auth_token is not None

    if not namespace:
        namespace = simple_prompt(
            'What should your namespace be? (Should only contain lower-case letters, numbers, or "-", e.g. "janedoe")')

    assert namespace is not None

    return RancherDetails(endpoint=rancher_endpoint, auth_token=auth_token, namespace=namespace)


_MESSAGE_401 = 'Unauthorized. Check your bearer token and try again'  # pylint: disable=invalid-name
_MESSAGE_404 = 'Invalid URL. Check your Rancher endpoint and try again'  # pylint: disable=invalid-name
# pylint: disable=invalid-name
_MESSAGE_403 = 'Forbidden. Try creating a new auth token. If the issue persists, notify your cluster administrator.'
# pylint: disable=invalid-name
_MESSAGE_500 = ('Server error. MosaicML platform had an issue processing your request. '
                'Please notify your cluster administrator.')


class ClusterInfo(NamedTuple):
    id: str
    name: str


def retrieve_clusters(
    endpoint: str,
    auth_token: str,
) -> List[ClusterInfo]:

    _GET_CLUSTER_MESSAGE = 'Error retrieving cluster info'

    headers = {'Authorization': 'Bearer ' + auth_token}

    resp = requests.request('GET', endpoint + '/v3/clusters', headers=headers, timeout=10)

    if resp.status_code == 401:
        raise RuntimeError(f'{_GET_CLUSTER_MESSAGE}: {_MESSAGE_401}')

    if resp.status_code == 404:
        raise RuntimeError(f'{_GET_CLUSTER_MESSAGE}: {_MESSAGE_404}')

    return [ClusterInfo(item['id'], item['name']) for item in resp.json()['data'] if item['state'] == 'active']


class ProjectInfo(NamedTuple):
    id: str
    name: str
    cluster: str
    display_name: str


def retrieve_projects(
    endpoint: str,
    auth_token: str,
) -> List[ProjectInfo]:

    headers = {'Authorization': 'Bearer ' + auth_token}

    resp = requests.request('GET', endpoint + '/v3/projects', headers=headers, timeout=10)

    _GET_PROJECTS_MESSAGE = 'Error getting available projects'
    if resp.status_code == 401:
        raise RuntimeError(f'{_GET_PROJECTS_MESSAGE}: {_MESSAGE_401}')

    if resp.status_code == 404:
        raise RuntimeError(f'{_GET_PROJECTS_MESSAGE}: {_MESSAGE_404}')

    return [
        ProjectInfo(proj['id'], proj['id'].split(':')[1], proj['id'].split(':')[0], proj['name'])
        for proj in resp.json()['data']
    ]


def configure_namespaces(
    endpoint: str,
    auth_token: str,
    projects: List[ProjectInfo],
    namespace_name: str,
):
    headers = {'Authorization': 'Bearer ' + auth_token}

    for project in projects:
        payload = {
            'type': 'namespace',
            'metadata': {
                'annotations': {
                    'field.cattle.io/containerDefaultResourceLimit': '{}',
                },
                'labels': {},
            },
            'disableOpenApiValidation': False
        }

        payload['metadata']['annotations']['field.cattle.io/projectId'] = project.id
        payload['metadata']['labels']['field.cattle.io/projectId'] = project.name
        payload['metadata']['name'] = namespace_name

        resp = requests.request('POST',
                                endpoint + '/k8s/clusters/' + project.cluster + '/v1/namespaces',
                                headers=headers,
                                data=json.dumps(payload),
                                timeout=10)

        _CREATE_NAMESPACE_MESSAGE = f'Error creating namespace {namespace_name} on cluster {project.cluster}'
        if resp.status_code == 401:
            raise RuntimeError(f'{_CREATE_NAMESPACE_MESSAGE}: {_MESSAGE_401}')

        if resp.status_code == 403:
            raise RuntimeError(f'{_CREATE_NAMESPACE_MESSAGE}: {_MESSAGE_403}')

        if resp.status_code == 404:
            raise RuntimeError(f'{_CREATE_NAMESPACE_MESSAGE}: {_MESSAGE_404}')

        if resp.status_code == 500:
            raise RuntimeError(f'{_CREATE_NAMESPACE_MESSAGE}: {_MESSAGE_500}')


def generate_cluster_config(
    endpoint: str,
    auth_token: str,
    clusters: List[ClusterInfo],
    namespace: Optional[str] = None,
):

    headers = {'Authorization': 'Bearer ' + auth_token}

    MCLI_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if MCLI_KUBECONFIG.exists():
        with open(MCLI_KUBECONFIG, 'r', encoding='utf-8') as f:
            kubeconfig = yaml.safe_load(f)
    else:
        kubeconfig = {
            'apiVersion': 'v1',
            'kind': 'Config',
            'clusters': [],
            'users': [],
            'contexts': [],
        }

    for cluster in clusters:
        updated_cluster = False
        updated_user = False
        updated_context = False

        if cluster.id == 'local':
            continue

        resp = requests.request('POST',
                                endpoint + '/v3/clusters/' + cluster.id + '?action=generateKubeconfig',
                                headers=headers,
                                timeout=10)

        _GET_KUBECONFIG_MESSAGE = f'Error creating kubeconfig for cluster {cluster.name}'
        if resp.status_code == 401:
            raise RuntimeError(f'{_GET_KUBECONFIG_MESSAGE}: {_MESSAGE_404}')

        if resp.status_code == 404:
            raise RuntimeError(f'{_GET_KUBECONFIG_MESSAGE}: {_MESSAGE_404}')

        if resp.status_code == 500:
            raise RuntimeError(f'{_GET_KUBECONFIG_MESSAGE}: {_MESSAGE_500}')

        config = yaml.safe_load(resp.json()['config'])

        if namespace:
            config['contexts'][0]['context']['namespace'] = namespace

        for cl in kubeconfig['clusters']:
            if cl['name'] == config['clusters'][0]['name']:
                cl['cluster'] = config['clusters'][0]['cluster']
                updated_cluster = True
                break
        for cl in kubeconfig['users']:
            if cl['name'] == config['users'][0]['name']:
                cl['user'] = config['users'][0]['user']
                updated_user = True
                break
        for cl in kubeconfig['contexts']:
            if cl['name'] == config['contexts'][0]['name']:
                cl['context'] = config['contexts'][0]['context']
                updated_context = True
                break

        if not updated_cluster:
            kubeconfig['clusters'].append(config['clusters'][0])

        if not updated_user:
            kubeconfig['users'].append(config['users'][0])

        if not updated_context:
            kubeconfig['contexts'].append(config['contexts'][0])

        kubeconfig.setdefault('current-context', kubeconfig['contexts'][0]['name'])

        with open(MCLI_KUBECONFIG, 'w', encoding='utf-8') as f:
            yaml.safe_dump(kubeconfig, f)


def initialize_k8s(
    auth_token: Optional[str] = None,
    rancher_endpoint: Optional[str] = None,
    namespace: Optional[str] = None,
    **kwargs,
) -> int:
    # pylint: disable=too-many-statements
    del kwargs

    try:
        if rancher_endpoint:
            # Ensure no trailing '/'.
            rancher_endpoint = rancher_endpoint.rstrip('/')
            validate_rancher_endpoint(rancher_endpoint)

        if namespace:
            result = validate_rfc1123_name(namespace)
            if not result:
                raise RuntimeError(result.message)

        details = fill_rancher_values(auth_token=auth_token, rancher_endpoint=rancher_endpoint, namespace=namespace)
        rancher_endpoint, auth_token, namespace = details

        # Retrieve all available clusters
        with console_status('Retrieving clusters...'):
            clusters = retrieve_clusters(rancher_endpoint, auth_token)
        if clusters:
            logger.info(f'{OK} Found {len(clusters)} clusters that you have access to')
        else:
            logger.error(f'{FAIL} No clusters found. Please double-check that you have access to clusters in '
                         'the MosaicML platform')
            return 1

        # Setup namespace
        with console_status('Getting available projects...'):
            projects = retrieve_projects(rancher_endpoint, auth_token)

        # Get unique projects
        cluster_project_map: Dict[str, List[ProjectInfo]] = {}
        for project in projects:
            cluster_project_map.setdefault(project.cluster, []).append(project)
        unique_projects: List[ProjectInfo] = []
        for cluster_id, project_list in cluster_project_map.items():
            chosen = project_list[0]
            unique_projects.append(chosen)
            if len(project_list) > 1:
                cluster_name = {cluster.id: cluster.name for cluster in clusters}.get(cluster_id)
                assert cluster_name is not None
                logger.warning(
                    f'Found {len(project_list)} projects for cluster {bold(cluster_name)}. '
                    f'Creating namespace in the first one: {chosen.display_name}. If you need to use a different '
                    'project, please move the namespace in Rancher.')

        with console_status(f'Setting up namespace {namespace}...'):
            configure_namespaces(rancher_endpoint, auth_token, unique_projects, namespace)
        logger.info(f'{OK} Configured namespace {namespace} in {len(clusters)} available clusters')

        # Generate kubeconfig file from clusters
        with console_status('Generating custom kubeconfig file...'):
            generate_cluster_config(rancher_endpoint, auth_token, clusters, namespace)
        logger.info(f'{OK} Created a new Kubernetes config file at: {MCLI_KUBECONFIG}')

        # Suggest next steps
        cluster_names = ', '.join(bold(cluster.name) for cluster in clusters)
        logger.info(f'You now have access to {bold(str(len(clusters)))} new clusters: '
                    f'{cluster_names}')

    except RuntimeError as e:
        logger.error(f'{FAIL} {e}')
        return 1

    return 0


def add_init_kube_parser(subparser: argparse._SubParsersAction):
    kube_init_parser: argparse.ArgumentParser = subparser.add_parser(
        'init-kube',
        help='Configure your Kubernetes clusters in the MosaicML platform',
    )
    kube_init_parser.add_argument('--auth-token', default=None, help='Your bearer token')
    kube_init_parser.add_argument(
        '--endpoint',
        dest='rancher_endpoint',
        default=None,
        help=f'The Rancher instance URL of the form: {RANCHER_ENDPOINT_PATTERN}. This is only required for use cases '
        'with advanced configuration requirements.',
    )
    kube_init_parser.add_argument(
        '--namespace',
        default=None,
        help='Your namespace within the clusters. If it '
        'doesn\'t exist, it\'ll be created for you.',
    )
    kube_init_parser.set_defaults(func=initialize_k8s)
    return kube_init_parser
