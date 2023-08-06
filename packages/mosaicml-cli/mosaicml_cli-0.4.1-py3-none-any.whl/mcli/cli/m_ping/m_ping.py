""" mcli ping entrypoint """
import argparse
import logging
from pprint import pprint
from typing import Callable, Union, cast

import validators

from mcli.api.exceptions import MAPIException
from mcli.api.model.inference_deployment import InferenceDeployment
from mcli.cli.common.deployment_filters import get_deployments_with_filters
from mcli.sdk import ping_inference_deployment
from mcli.utils.utils_logging import FAIL, err_console

logger = logging.getLogger(__name__)


def ping(
    deployment: str,
    **kwargs,
) -> int:
    del kwargs
    try:
        deployment_obj_or_url: Union[InferenceDeployment, str] = deployment
        validate_url = cast(Callable[[str], bool], validators.url)
        if not deployment_obj_or_url or not validate_url(deployment):
            # if a url is not passed in then lookup the deployment and get the name
            deployment_objs = get_deployments_with_filters(name_filter=[deployment])
            if len(deployment_objs) == 0:

                if not deployment:
                    err_console.print("No inference deployments found.")
                else:
                    err_console.log(f'No inference deployment found with name {deployment}.')
                return 1

            deployment_obj_or_url = deployment_objs[0]

        resp = ping_inference_deployment(deployment_obj_or_url)
        name_or_url = deployment_obj_or_url if isinstance(deployment_obj_or_url, str) else deployment_obj_or_url.name
        print(f'{name_or_url}\'s status:')
        pprint(resp)
        return 0
    except RuntimeError as e:
        logger.error(f'{FAIL} {e}')
        return 1
    except MAPIException as e:
        logger.error(f'{FAIL} {e}')
        return 1


def add_ping_parser(subparser: argparse._SubParsersAction):
    ping_parser: argparse.ArgumentParser = subparser.add_parser(
        'ping',
        help='Ping a inference deployment in the MosaicML platform for health metrics',
    )
    ping_parser.add_argument('deployment', metavar='DEPLOYMENT', help='The name or url of the inference deployment.')

    ping_parser.set_defaults(func=ping)
