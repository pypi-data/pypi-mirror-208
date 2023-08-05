"""Implementation of mcli get runs"""
from __future__ import annotations

import argparse
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Generator, List, Optional, Tuple

from mcli import config
from mcli.api.exceptions import cli_error_handler
from mcli.cli.common.run_filters import configure_submission_filter_argparser, get_runs_with_filters
from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay, format_timestamp
from mcli.sdk import Run
from mcli.utils.utils_cli import comma_separated
from mcli.utils.utils_logging import WARN
from mcli.utils.utils_run_status import RunStatus

DEFAULT_DISPLAY_LIMIT = 50

logger = logging.getLogger(__name__)

GPUS_PER_NODE = 8


class RunColumns(Enum):
    ID = 'id'
    NAME = 'name'
    USER = 'user'
    CLUSTER = 'cluster'
    INSTANCE = 'instance'
    NODES = 'nodes'
    CREATED_TIME = 'created_time'
    START_TIME = 'start_time'
    END_TIME = 'end_time'
    STATUS = 'status'


@dataclass
class RunDisplayItem(MCLIDisplayItem):
    """Tuple that extracts run data for display purposes.
    """
    name: str
    nodes: str
    created_time: str
    start_time: str
    end_time: str
    status: str
    user: str
    instance: str
    cluster: Optional[str] = None
    id: Optional[str] = None

    @classmethod
    def from_run(cls, run: Run, include_ids: bool = False) -> RunDisplayItem:
        display_status = run.status.display_name
        if run.reason:
            display_status = f"{display_status} ({run.reason})"
        instance, nodes = get_instance_name_and_nodes(run)
        extracted: Dict[str, str] = {
            RunColumns.NAME.value: run.name,
            RunColumns.USER.value: run.created_by,
            RunColumns.CLUSTER.value: run.config.cluster,
            RunColumns.INSTANCE.value: instance,
            RunColumns.NODES.value: str(nodes),
            RunColumns.CREATED_TIME.value: format_timestamp(run.created_at),
            RunColumns.START_TIME.value: format_timestamp(run.started_at),
            RunColumns.END_TIME.value: format_timestamp(run.completed_at),
            RunColumns.STATUS.value: display_status,
        }
        if include_ids:
            extracted[RunColumns.ID.value] = run.run_uid

        return RunDisplayItem(**extracted)


class MCLIRunDisplay(MCLIGetDisplay):
    """Display manager for runs
    """

    def __init__(self, models: List[Run], include_ids: bool = False):
        self.models = sorted(models, key=lambda x: x.created_at, reverse=True)
        self.include_ids = include_ids

    @property
    def override_column_ordering(self) -> Optional[List[str]]:
        cols = []
        for c in RunColumns:
            if c == RunColumns.NAME:
                continue
            if not self.include_ids and c == RunColumns.ID:
                continue
            cols.append(c.value)
        return cols

    def __iter__(self) -> Generator[RunDisplayItem, None, None]:
        for model in self.models:
            item = RunDisplayItem.from_run(model, include_ids=self.include_ids)
            yield item


def get_instance_name_and_nodes(run: Run) -> Tuple[str, int]:
    """Get the run's instance name and number of nodes

    We'll try to create a human-readable name based on the gpu number and type (ie 8x v100),
    if possible.

    With the addition of `compute` to the run config, all values should be filled in, so much
    of the logic here is for older runs. These have a limited set of possible values, so we
    make some assumptions which should largely be correct.

    Args:
        run (Run): a Run

    Returns:
        Tuple[str, int]: The instance name and number of nodes
    """

    # Extract GPU Type
    # Default to 'cpu' type
    gpu_type = 'cpu'
    if run.config.compute.get('gpu_type', None):
        assert 'gpu_type' in run.config.compute  # for the linter
        gpu_type = run.config.compute['gpu_type']
        assert gpu_type is not None  # Also for the linter...
    elif run.config.gpu_type:
        gpu_type = run.config.gpu_type

    # Convert 'None' to 'cpu'
    if gpu_type.lower() == 'none':
        gpu_type = 'cpu'

    # Extract GPU Number
    # Default to 0 because some older runs may only set gpu type, which was probably "None"
    total_gpus = 0
    if 'gpus' in run.config.compute and run.config.compute['gpus'] is not None:
        total_gpus = run.config.compute['gpus']
    elif run.config.gpu_num is not None:
        total_gpus = run.config.gpu_num

    # Get the instance type as a fallback
    instance = run.config.compute.get('instance', None)

    # Get the number of nodes
    nodes = run.config.compute.get('nodes', None)
    if nodes is not None:
        # Trim to gpus per node
        gpus = int(total_gpus / nodes)
    elif total_gpus > GPUS_PER_NODE:
        # If we have more than 8 gpus, we can reasonably assume we're on multinode
        # This assumes 8 gpus per node, which should be valid for all old runs
        nodes = math.ceil(total_gpus / GPUS_PER_NODE)
        gpus = GPUS_PER_NODE
    else:
        nodes = 1
        gpus = total_gpus

    if gpu_type != 'cpu':
        # Prefer the gpu type as a description, if available
        return f"{gpus}x {gpu_type.lower()}", nodes
    elif instance:
        # Fall back on instance type (especially for cpu instances)
        return instance, nodes
    elif gpu_type == 'cpu':
        # Otherwise just use "cpu"
        return gpu_type, nodes
    else:
        # Last resort, go with unknown
        return 'unknown', nodes


@cli_error_handler('mcli get runs')
def cli_get_runs(
    name_filter: Optional[List[str]] = None,
    cluster_filter: Optional[List[str]] = None,
    before_filter: Optional[str] = None,
    after_filter: Optional[str] = None,
    gpu_type_filter: Optional[List[str]] = None,
    gpu_num_filter: Optional[List[int]] = None,
    status_filter: Optional[List[RunStatus]] = None,
    output: OutputDisplay = OutputDisplay.TABLE,
    include_ids: bool = False,
    latest: bool = False,
    user_filter: Optional[List[str]] = None,
    limit: Optional[int] = DEFAULT_DISPLAY_LIMIT,
    **kwargs,
) -> int:
    """Get a table of ongoing and completed runs
    """
    del kwargs

    runs = get_runs_with_filters(
        name_filter=name_filter,
        cluster_filter=cluster_filter,
        before_filter=before_filter,
        after_filter=after_filter,
        gpu_type_filter=gpu_type_filter,
        gpu_num_filter=gpu_num_filter,
        status_filter=status_filter,
        latest=latest,
        user_filter=user_filter,
        limit=limit,
    )

    display = MCLIRunDisplay(runs, include_ids=include_ids)
    display.print(output)

    if len(runs) == DEFAULT_DISPLAY_LIMIT:
        logger.warning(f'{WARN} Run view shows only the last {DEFAULT_DISPLAY_LIMIT} runs and may be truncated. '
                       'Use --limit to increase the number of runs displayed.')
    return 0


def get_runs_argparser(subparsers: argparse._SubParsersAction):
    """Configures the ``mcli get runs`` argparser
    """

    run_examples: str = """Examples:
    $ mcli get runs

    NAME                         CLUSTER    GPU_TYPE      GPU_NUM      CREATED_TIME     USER               STATUS
    run-foo                      c-1        g0-type       8            05/06/22 1:58pm  abc@gmail.com      Completed
    run-bar                      c-2        g0-type       1            05/06/22 1:57pm  abc@gmail.com      Completed

    $ mcli get runs --user xyz@gmail.com
    NAME                         CLUSTER    GPU_TYPE      GPU_NUM      CREATED_TIME     USER               STATUS
    run-xyz-1                    c-1        g0-type       8            05/06/22 1:58pm  xyz@gmail.com      Completed
    run-xyz-2                    c-2        g0-type       1            05/06/22 1:57pm  xyz@gmail.com      Completed
    """
    runs_parser = subparsers.add_parser('runs',
                                        aliases=['run'],
                                        help='Get information on all of your existing runs across all clusters.',
                                        epilog=run_examples,
                                        formatter_class=argparse.RawDescriptionHelpFormatter)

    configure_submission_filter_argparser('get', runs_parser, include_all=False)
    runs_parser.set_defaults(func=cli_get_runs)

    runs_parser.add_argument('--ids',
                             action='store_true',
                             dest='include_ids',
                             default=config.ADMIN_MODE,
                             help='Include the run ids in the output')

    def user(value: str):
        return comma_separated(value)

    runs_parser.add_argument(
        '-u',
        '--user',
        dest='user_filter',
        default=None,
        metavar='User',
        type=user,
        help='Fetch the runs created by a user in your organization with their email address. '
        'Multiple users should be specified using a comma-separated list, '
        'e.g. "alice@gmail.com,bob@gmail.com"',
    )

    def limit(value: str) -> Optional[int]:
        if value.lower() == 'none':
            return None

        return int(value)

    runs_parser.add_argument(
        '--limit',
        help='Maximum number of runs to return. Runs will be sorted by creation time. '
        f'Default: {DEFAULT_DISPLAY_LIMIT}',
        default=DEFAULT_DISPLAY_LIMIT,
        type=limit,
    )
    return runs_parser
