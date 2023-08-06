"""Implementation of mcli describe run"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Generator, List, Optional, Tuple, TypeVar

from rich.table import Table

from mcli.api.exceptions import cli_error_handler
from mcli.api.model.run import Node, Run, RunLifecycle
from mcli.cli.common.run_filters import get_runs_with_filters
from mcli.cli.m_get.display import (MCLIDisplayItem, MCLIGetDisplay, OutputDisplay, create_vertical_display_table,
                                    format_timestamp)
from mcli.models.run_config import DEFAULT_PRIORITY_NAME, ComputeConfig
from mcli.utils.utils_logging import FormatString, console, format_string, print_timedelta, seconds_to_str

logger = logging.getLogger(__name__)

DISPLAY_RUN_STATUSES = ['PENDING', 'RUNNING', 'COMPLETED']


class DisplayRunStatus(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'


class DescribeRunDetailColumns(Enum):
    NAME = 'name'
    RUN_ID = 'run_uid'
    LAST_ATTEMPT_ID = 'last_attempt_id'
    CLUSTER = 'cluster'
    GPU_TYPE = 'gpu_type'
    GPU_NUM = 'gpu_num'
    CPUS = 'cpus'
    IMAGE = 'image'
    PRIORITY = 'priority'


class DescribeRunOriginalInputColumns(Enum):
    SUBMITTED_CONFIG = 'submitted_config'


RUN_DETAIL_DISPLAY_NAMES = ['Run Name', 'Run ID', 'Last Attempt ID', 'Cluster', 'Image', 'GPU Type', 'GPU Num']

RUN_LIFECYCLE_DISPLAY_NAMES = ['Status', 'Reached At', 'Duration', 'Reason']
RUN_NODES_DISPLAY_NAMES = ['Node Name']
SUBMITTED_CONFIG = ['Run Config']


@dataclass
class DescribeRunDetailDisplayItem(MCLIDisplayItem):
    """Tuple that extracts detailed run data for display purposes"""
    name: str
    run_uid: str
    last_attempt_id: str
    cluster: str
    image: str
    last_attempt_id: str
    priority: str

    @classmethod
    def from_run(cls, run: Run) -> DescribeRunDetailDisplayItem:
        priority = run.config.scheduling.get('priority', None) or DEFAULT_PRIORITY_NAME
        if priority and priority.lower() == 'default':
            priority = DEFAULT_PRIORITY_NAME

        extracted: Dict[str, Any] = {
            DescribeRunDetailColumns.NAME.value: run.config.name,
            DescribeRunDetailColumns.RUN_ID.value: run.run_uid,
            DescribeRunDetailColumns.LAST_ATTEMPT_ID.value: run.last_attempt_id,
            DescribeRunDetailColumns.CLUSTER.value: run.config.cluster,
            DescribeRunDetailColumns.IMAGE.value: run.config.image,
            DescribeRunDetailColumns.PRIORITY.value: priority.lower(),
        }

        return DescribeRunDetailDisplayItem(**extracted)


@dataclass
class DescribeRunLifecycleDisplayItem(MCLIDisplayItem):
    """Tuple that extracts run data for run lifecycle display purposes"""
    attempt: str
    status: str
    reached_at: str
    duration: str
    reason: str


@dataclass
class DescribeRunMetadataDisplayItem(MCLIDisplayItem):
    """Tuple that extracts run metadata for display purposes"""

    key: str
    value: str


@dataclass
class MCLIDescribeRunNodeDisplayItem(MCLIDisplayItem):
    """Tuple that extracts run data for run node display purposes"""
    rank: int
    name: str


# Displays
class MCLIDescribeRunDetailsDisplay(MCLIGetDisplay):
    """ Vertical table view of run details """

    def __init__(self, models: List[Run]):
        self.models = sorted(models, key=lambda x: x.created_at, reverse=True)

    @property
    def index_label(self) -> str:
        return ""

    def create_custom_table(self, columns: List[str], data: List[Tuple[Any, ...]], names: List[str]) -> Optional[Table]:
        return create_vertical_display_table(data=data, columns=RUN_DETAIL_DISPLAY_NAMES)

    def __iter__(self) -> Generator[DescribeRunDetailDisplayItem, None, None]:
        for model in self.models:
            item = DescribeRunDetailDisplayItem.from_run(model)
            yield item


class MCLIDescribeRunLifecycleDisplay(MCLIGetDisplay):
    """ Horizontal table view of run lifecycle """

    def __init__(self, model: List[RunLifecycle]):
        self.model = model
        self.include_reason_in_display = any(m.reason for m in model)

    @property
    def custom_column_names(self) -> List[str]:
        if self.include_reason_in_display:
            return RUN_LIFECYCLE_DISPLAY_NAMES
        else:
            return RUN_LIFECYCLE_DISPLAY_NAMES[:-1]

    def __iter__(self) -> Generator[DescribeRunLifecycleDisplayItem, None, None]:
        last_index: Optional[int] = None
        for e in self.model:
            duration = ''
            if e.started_at and e.ended_at:
                duration = print_timedelta(e.ended_at - e.started_at)
            yield DescribeRunLifecycleDisplayItem(
                attempt=str(e.attempt_id) if last_index != e.attempt_id else '',
                status=e.status.display_name,
                reached_at=format_timestamp(e.started_at),
                duration=duration,
                reason=e.reason or '',
            )
            last_index = e.attempt_id

    @property
    def index_label(self) -> str:
        return 'attempt'


class MCLIDescribeRunMetadataDisplay(MCLIGetDisplay):
    """ Vertical table view of run metadata """

    def __init__(self, metadata: Dict[str, Any]):
        self.columns = sorted(metadata.keys())
        self.metadata = metadata

    @property
    def index_label(self) -> str:
        return "key"

    def __iter__(self) -> Generator[DescribeRunMetadataDisplayItem, None, None]:
        for k in self.columns:
            item = DescribeRunMetadataDisplayItem(key=k, value=self.metadata[k])
            yield item


class MCLIDescribeRunNodeDisplay(MCLIGetDisplay):
    """ Horizontal table view of run node """

    def __init__(self, nodes: List[Node]):
        self.nodes = sorted(nodes, key=lambda x: x.rank)

    @property
    def custom_column_names(self) -> List[str]:
        return RUN_NODES_DISPLAY_NAMES

    def __iter__(self) -> Generator[MCLIDescribeRunNodeDisplayItem, None, None]:
        for n in self.nodes:
            yield MCLIDescribeRunNodeDisplayItem(n.rank, n.name)

    @property
    def index_label(self) -> str:
        return 'rank'


T = TypeVar('T')


def compute_or_deprecated(compute: ComputeConfig, key: str, deprecated: T) -> Optional[T]:
    from_compute = compute.get(key, None)
    if from_compute is not None:
        return from_compute
    return deprecated


@dataclass
class DescribeComputeRequests():
    """Describer for compute requests"""
    cluster: Optional[str] = None
    gpu_type: Optional[str] = None
    gpus: Optional[int] = None
    cpus: Optional[int] = None
    instance: Optional[str] = None
    nodes: Optional[int] = None

    @property
    def display_names(self) -> Dict[str, str]:
        # Return display name mapping for table
        return {
            'cluster': 'Cluster',
            'gpu_type': 'GPU Type',
            'gpus': 'GPUs',
            'cpus': 'CPUs',
            'instance': 'Instance',
            'nodes': 'Nodes',
        }

    @classmethod
    def from_run(cls, run: Run) -> DescribeComputeRequests:
        return DescribeComputeRequests(
            cluster=compute_or_deprecated(run.config.compute, 'cluster', run.config.cluster),
            gpu_type=compute_or_deprecated(run.config.compute, 'gpu_type', run.config.gpu_type),
            gpus=compute_or_deprecated(run.config.compute, 'gpus', run.config.gpu_num),
            cpus=compute_or_deprecated(run.config.compute, 'cpus', run.config.cpus),
            instance=run.config.compute.get('instance', None),
            nodes=run.config.compute.get('nodes', None),
        )

    def to_table(self) -> Table:
        data = {self.display_names.get(k, k.capitalize()): str(v) for k, v in asdict(self).items() if v is not None}
        columns = list(data.keys())
        values = [tuple(data.values())]
        return create_vertical_display_table(data=values, columns=columns)


@cli_error_handler("mcli describe run")
def describe_run(run_name: Optional[str], output: OutputDisplay = OutputDisplay.TABLE, **kwargs):
    """
    Fetches more details of a Run
    """
    del kwargs

    latest = not run_name
    name_filter = [run_name] if run_name else []

    runs = get_runs_with_filters(name_filter=name_filter, latest=latest, include_details=True)

    if len(runs) == 0:
        print(f'No runs found with name: {run_name}')
        return
    run = runs[0]

    # Run details section
    print(format_string('Run Details', FormatString.BOLD))
    metadata_display = MCLIDescribeRunDetailsDisplay([run])
    metadata_display.print(output)
    print()

    # Compute requests section
    print(format_string('Compute Requests', FormatString.BOLD))
    compute_display = DescribeComputeRequests.from_run(run)
    console.print(compute_display.to_table())
    print()

    # Run lifecycle section
    print(format_string('Run Lifecycle', FormatString.BOLD))
    lifecycle_display = MCLIDescribeRunLifecycleDisplay(run.lifecycle)
    lifecycle_display.print(output)
    print()
    print(f'Total Attempts: {run.attempts:,}')
    print(f'Total time spent in Pending: {seconds_to_str(run.cumulative_pending_time)}')
    print(f'Total time spent in Running: {seconds_to_str(run.cumulative_running_time)}')
    print()

    if run.metadata:
        print(format_string('Run Metadata', FormatString.BOLD))
        metadata_display = MCLIDescribeRunMetadataDisplay(run.metadata)
        metadata_display.print(output)
        print()

    if run.nodes:
        print(format_string('Run Nodes', FormatString.BOLD))
        node_display = MCLIDescribeRunNodeDisplay(run.nodes)
        node_display.print(output)
        print()

    # Run original input section
    print(format_string('Submitted YAML', FormatString.BOLD))
    print(run.submitted_config)

    # TODO: cleanup code to print directly to console after parsing
    # wrap command string within a literal `representer` - dump long str as block
