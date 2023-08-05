"""CLI getter for deployments"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Generator, List, Optional

from mcli import config
from mcli.api.exceptions import cli_error_handler
from mcli.cli.common.deployment_filters import get_deployments_with_filters
from mcli.cli.common.run_filters import configure_submission_filter_argparser
from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay, format_timestamp
from mcli.sdk import InferenceDeployment
from mcli.utils.utils_cli import SubmissionType


class InferenceDeploymentColumns(Enum):
    ID = 'id'
    NAME = 'name'
    USER = 'user'
    CLUSTER = 'cluster'
    GPU_TYPE = 'gpu_type'
    GPU_NUM = 'gpu_num'
    CREATED_TIME = 'created_time'
    STATUS = 'status'


@dataclass
class InferenceDeploymentDisplayItem(MCLIDisplayItem):
    """Tuple that extracts deployment data for display purposes.
    """
    name: str
    gpu_num: str
    created_time: str
    status: str
    user: str
    cluster: Optional[str] = None
    gpu_type: Optional[str] = None
    id: Optional[str] = None

    @classmethod
    def from_deployment(cls,
                        deployment: InferenceDeployment,
                        include_ids: bool = False) -> InferenceDeploymentDisplayItem:
        extracted: Dict[str, str] = {
            InferenceDeploymentColumns.NAME.value: deployment.name,
            InferenceDeploymentColumns.USER.value: deployment.created_by,
            InferenceDeploymentColumns.GPU_NUM.value: str(deployment.config.gpu_num),
            InferenceDeploymentColumns.CREATED_TIME.value: format_timestamp(deployment.created_at),
            InferenceDeploymentColumns.STATUS.value: deployment.status,
            InferenceDeploymentColumns.CLUSTER.value: deployment.config.cluster,
            InferenceDeploymentColumns.GPU_TYPE.value: deployment.config.gpu_type
        }
        if include_ids:
            extracted[InferenceDeploymentColumns.ID.value] = deployment.deployment_uid

        return InferenceDeploymentDisplayItem(**extracted)


class InferenceDeploymentDisplay(MCLIGetDisplay):
    """`mcli get deployments` display class
    """

    def __init__(self, deployments: List[InferenceDeployment], include_ids: bool = False):
        self.deployments = sorted(deployments, key=lambda x: x.created_at, reverse=True)
        self.include_ids = include_ids

    @property
    def override_column_ordering(self) -> Optional[List[str]]:
        cols = []
        for c in InferenceDeploymentColumns:
            if c == InferenceDeploymentColumns.NAME:
                continue
            if not self.include_ids and c == InferenceDeploymentColumns.ID:
                continue
            cols.append(c.value)
        return cols

    def __iter__(self) -> Generator[InferenceDeploymentDisplayItem, None, None]:
        for deployment in self.deployments:
            yield InferenceDeploymentDisplayItem.from_deployment(deployment, self.include_ids)


@cli_error_handler('mcli get deployments')
def cli_get_deployments(
    name_filter: Optional[List[str]] = None,
    cluster_filter: Optional[List[str]] = None,
    before_filter: Optional[str] = None,
    after_filter: Optional[str] = None,
    gpu_type_filter: Optional[List[str]] = None,
    gpu_num_filter: Optional[List[int]] = None,
    status_filter: Optional[List[str]] = None,
    output: OutputDisplay = OutputDisplay.TABLE,
    include_ids: bool = False,
    **kwargs,
) -> int:
    """Get a table of ongoing and completed inference deployments
    """
    del kwargs

    deployments = get_deployments_with_filters(name_filter, cluster_filter, before_filter, after_filter,
                                               gpu_type_filter, gpu_num_filter, status_filter)

    display = InferenceDeploymentDisplay(deployments, include_ids=include_ids)
    display.print(output)

    return 0


def get_deployments_argparser(subparsers: argparse._SubParsersAction):
    """Configures the ``mcli get deployments`` argparser
    """

    deployment_examples: str = """Examples:
    $ mcli get deployments
    NAME                          CLUSTER     GPU_TYPE    GPU_NUM          CREATED_TIME     STATUS
    deploy-foo                      c-1        g0-type       8            05/06/22 1:58pm    Ready
    deploy-bar                      c-2        g0-type       1            05/06/22 1:57pm   Pending
    """
    deployments_parser = subparsers.add_parser(
        'deployments',
        aliases=['deployment'],
        help='Get information on all of your existing deployments across all clusters.',
        epilog=deployment_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    configure_submission_filter_argparser('get',
                                          deployments_parser,
                                          include_all=False,
                                          submission_type=SubmissionType.DEPLOYMENT)
    deployments_parser.set_defaults(func=cli_get_deployments)

    deployments_parser.add_argument('--ids',
                                    action='store_true',
                                    dest='include_ids',
                                    default=config.ADMIN_MODE,
                                    help='Include the deployment ids in the output')
    return deployments_parser
