""" mcli util helpers """

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any, Dict, Generator, List, Optional

import yaml
from rich.style import Style
from rich.table import Table

from mcli.api.cluster import get_clusters
from mcli.api.exceptions import MAPIErrorMessages, MAPIException, cli_error_handler
from mcli.api.model.cluster_details import ClusterDetails, ClusterUtilizationByRun
from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay
from mcli.utils.utils_logging import print_timedelta

logger = logging.getLogger(__name__)


def get_row_color(node: dict) -> Optional[str]:
    """Get the row color using the serialized NodeInfo data
    """
    gpus_used = int(node.get("gpus_used", 0))
    gpus_available = int(node.get("gpus_available", 0))

    if gpus_used == 0 and gpus_available == 0:
        return "bright_black"  # gray

    if gpus_available > 0:
        return "green"

    return None


@dataclass
class UtilizationInfo(MCLIDisplayItem):
    pos: int
    name: str
    run_name: str
    user: str
    age: str
    gpus: int
    priority: str


class UtilizationDisplay(MCLIGetDisplay):
    """Display information about the node
    """

    @property
    def index_label(self) -> str:
        if self.num_clusters == 1:
            return "run_name" if self.is_active_runs else "pos"
        else:
            return "name"

    def __init__(self, clusters: List[ClusterDetails], is_active_runs=True):
        self.clusters = clusters
        self.num_clusters = len({i.name for i in clusters})
        self.is_active_runs = is_active_runs

    def format_active_run_name(self, r: ClusterUtilizationByRun) -> str:
        return f'[cyan]{r.run_name}[/]'

    def format_pending_run_name(self, r: ClusterUtilizationByRun) -> str:
        return f'[yellow]{r.run_name}[/]'

    def format_priority(self, priority: Optional[str]) -> str:
        if not priority or priority == 'DEFAULT':
            return 'medium'
        return priority.lower()

    def get_list(self) -> List[Dict[str, Any]]:
        items = super().get_list()
        if not self.is_active_runs:
            # Pending runs should have the index included
            return items
        # Remove 'pos' from active runs
        for item in items:
            item.pop('pos', None)
        return items

    def __iter__(self) -> Generator[MCLIDisplayItem, None, None]:
        for cluster in self.clusters:
            assert cluster.utilization
            runs = cluster.utilization.active_by_user
            if not self.is_active_runs:
                runs = cluster.utilization.queued_by_user
            for i, by_user in enumerate(runs):
                # A priority value may not exist, so default it
                priority = self.format_priority(by_user.scheduling.get('priority', None))
                cluster_name = cluster.name
                if self.num_clusters == 1:
                    # Exclude cluster name from table completely when there's only one cluster
                    cluster_name = ''
                elif i > 0:
                    # Skip cluster name if it was the same as the previous
                    cluster_name = ''

                if self.is_active_runs:
                    name = self.format_active_run_name(by_user)
                else:
                    name = self.format_pending_run_name(by_user)

                yield UtilizationInfo(
                    i + 1,
                    cluster_name,
                    name,
                    by_user.user,
                    print_timedelta(datetime.now(timezone.utc) - by_user.created_at),
                    by_user.gpu_num,
                    priority,
                )


@dataclass
class ClusterInfo(MCLIDisplayItem):
    name: str
    gpu_instance_type: str
    gpus_available: int
    gpus_used: int
    gpus_total: int


class ClusterDisplay(MCLIGetDisplay):
    """Display information about the node
    """

    def __init__(self, clusters: List[ClusterDetails]):
        self.clusters = sorted(clusters)
        self.num_clusters = len({i.name for i in clusters})

    def __iter__(self) -> Generator[MCLIDisplayItem, None, None]:
        for cluster in self.clusters:
            assert cluster.utilization
            for inst in cluster.utilization.cluster_instance_utils:
                if inst.gpu_type == "None":
                    continue
                yield ClusterInfo(
                    cluster.name,
                    str(inst.gpus_per_node) + "x" + inst.gpu_type,
                    inst.gpus_available,
                    inst.gpus_used,
                    inst.gpus_total,
                )

    def to_table(self, items: List[Dict[str, Any]]) -> Table:
        """Overrides MCLIGetDisplay.to_table to have custom node colors by row using rich style
        """

        def _to_str(obj: Any) -> str:
            return yaml.safe_dump(obj, default_flow_style=None).strip() if not isinstance(obj, str) else obj

        column_names = self.override_column_ordering or [key for key, val in items[0].items() if val and key != 'name']

        data_table = Table(box=None, pad_edge=False)
        data_table.add_column('NAME', justify='left', no_wrap=True)

        for column_name in column_names:
            data_table.add_column(column_name.upper())

        for item in items:
            row_args = {}
            data_row = tuple(_to_str(item[key]) for key in column_names)
            color = get_row_color(item)
            if color is not None:
                row_args["style"] = Style(color=color)
            data_table.add_row(item['name'], *data_row, **row_args)

        return data_table


@cli_error_handler('mcli util')
def get_util(clusters: Optional[List[str]] = None, hide_users: bool = False, **kwargs) -> int:
    del kwargs
    try:
        c = get_clusters(clusters=clusters, include_utilization=True)
    except MAPIException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            e.message = MAPIErrorMessages.NOT_FOUND_CLUSTER.value
        raise e

    if len(c) == 0:
        raise MAPIException(HTTPStatus.NOT_FOUND, MAPIErrorMessages.NOT_FOUND_CLUSTER.value)

    agg = ''
    if len({cluster.name for cluster in c}) > 1:
        agg = ' by Cluster'
    print(f'GPU Instances{agg}:')
    cluster_display = ClusterDisplay(c)
    cluster_display.print(OutputDisplay.TABLE)

    if not hide_users:
        print(f'\nActive Runs{agg}:')
        active_runs_display = UtilizationDisplay(c, is_active_runs=True)
        active_runs_display.print(OutputDisplay.TABLE)
        print(f'\nQueued Runs{agg}:')
        queued_runs_display = UtilizationDisplay(c, is_active_runs=False)
        queued_runs_display.print(OutputDisplay.TABLE)

    return 0
