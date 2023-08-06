"""mcli predict entrypoint"""
import argparse
import logging
from pprint import pprint
from typing import Any, Callable, Dict, Union, cast

import validators
import yaml

from mcli.api.exceptions import MAPIException
from mcli.api.model.inference_deployment import InferenceDeployment
from mcli.cli.common.deployment_filters import get_deployments_with_filters
from mcli.sdk import predict
from mcli.utils.utils_logging import FAIL, err_console

logger = logging.getLogger(__name__)


def predict_cli(
    inputs: Dict[str, Any],
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
                    err_console.print(f'No inference deployment found with name {deployment}.')
                return 1

            deployment_obj_or_url = deployment_objs[0]

        resp = predict(deployment_obj_or_url, inputs=inputs)
        name_or_url = deployment_obj_or_url if isinstance(deployment_obj_or_url, str) else deployment_obj_or_url.name
        print(f'{name_or_url}\'s prediction results:')
        pprint(resp)
        return 0
    except RuntimeError as e:
        logger.error(f'{FAIL} {e}')
        return 1
    except MAPIException as e:
        logger.error(f'{FAIL} {e}')
        return 1


def add_predict_parser(subparser: argparse._SubParsersAction):
    predict_parser: argparse.ArgumentParser = subparser.add_parser(
        'predict',
        help='Run prediction on a model in the MosaicML Cloud with given inputs. Returns forward pass result',
    )
    predict_parser.add_argument('deployment',
                                metavar='DEPLOYMENT',
                                help='The name or url of the deployment to run inference on')

    predict_parser.add_argument(
        '--input',
        '--inputs',
        '-i',
        dest='inputs',
        required=True,
        nargs="?",
        type=yaml.safe_load,
        metavar='INPUT',
        help='Input values to run forward pass on. Input values must be JSON-serializable and have string keys.',
    )

    predict_parser.set_defaults(func=predict_cli)
