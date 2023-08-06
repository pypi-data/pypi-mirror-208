"""CLI getter for clusters"""
import logging
from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional

from rich.table import Table

from mcli.api.cluster import get_clusters as api_get_cluster
from mcli.api.exceptions import cli_error_handler
from mcli.api.model.cluster_details import ClusterDetails
from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay, create_display_table

logger = logging.getLogger(__name__)


def get_gpu_description(gpus: int, nodes: int, allow_fractional: bool, allow_multinode: bool) -> str:
    """Get a string showing possible `gpus` values for the instance

    Args:
        gpus (int): Number of GPUs per node for the instance
        nodes (int): Number of nodes of the instance type that are available
        allow_fractional (bool): Whether fractional nodes can be allocated
        allow_multinode (bool): Whether multinode runs are allowed

    Returns:
        str: Useful string of gpu values

    Examples:
    For only single node runs with fractional enabled:
    >>> get_gpu_description(8, 1, True, False)
    "≤8"

    For multinode runs with 10 nodes available:
    >>> get_gpu_description(8, 10, False, True)
    "8,16,...,80"
    """
    if nodes < 1:
        return '-'

    if gpus == 0:
        return '0'

    options: List[str] = []
    if allow_fractional:
        options.append(f'≤{gpus}')
    else:
        options.append(f'{gpus}')

    if not allow_multinode or nodes == 1:
        return options[0]

    options.append(f'{2 * gpus}')
    if nodes > 3:
        options.extend(['...', f'{nodes * gpus}'])
    elif nodes == 3:
        options.append(f'{3 * gpus}')

    return ','.join(options)


def get_nodes_description(nodes: int, allow_multinode: bool) -> str:
    """Get a string showing possible `nodes` values for the instance
    """
    if nodes == 0:
        return '-'
    if not allow_multinode or nodes == 1:
        return '1'
    else:
        return f'≤{nodes}'


@dataclass
class ClusterDisplayItem(MCLIDisplayItem):
    # Cluster columns
    id: Optional[str]
    name: str
    provider: str

    # GPU columns
    gpu_type: str
    gpus: str

    # Instance columns
    instance: str
    nodes: str


GPU_COLUMNS = ['gpu_type', 'gpus']
INSTANCE_COLUMNS = ['instance', 'nodes']
SEP_HEADER = ['']
SEP = ['│']


class ClusterDisplay(MCLIGetDisplay):
    """`mcli get cluster` display class
    """

    def __init__(self, cluster: List[ClusterDetails], include_ids: bool = False):
        self.cluster = sorted(cluster)
        self.include_ids = include_ids

    def __iter__(self) -> Generator[ClusterDisplayItem, None, None]:
        for c in self.cluster:
            for instance in sorted(c.cluster_instances, reverse=True):

                # cpu instance sometimes captures non-worker nodes, so we'll just set
                # the value to 1 (unless it was 0)
                nodes = get_nodes_description(instance.nodes, c.allow_multinode)
                if instance.name == 'cpu' and nodes != '-':
                    nodes = '1'

                yield ClusterDisplayItem(
                    id=c.id if self.include_ids else None,
                    name=c.name,
                    provider=c.provider,
                    instance=instance.name,
                    nodes=nodes,
                    gpu_type=instance.gpu_type.lower(),
                    gpus=get_gpu_description(
                        instance.gpus,
                        instance.nodes,
                        c.allow_fractional,
                        c.allow_multinode,
                    ),
                )

    def to_name(self, items: List[Dict[str, Any]]) -> List[str]:
        """Customized name output for clusters that removes duplicates
        """
        return list({item['name']: None for item in items}.keys())

    def to_table(self, items: List[Dict[str, Any]]) -> Table:
        """Customized table output for clusters that includes a separator between
        gpu details and instance details
        """

        # Get cluster columns and instance columns
        # Cluster columns will be suppressed if repeated
        cluster_columns, gpu_columns, instance_columns = [], [], []
        reference = items[0]
        for k in reference:
            if k == 'name':
                continue
            if k == 'id' and not self.include_ids:
                continue
            if k in GPU_COLUMNS:
                gpu_columns.append(k)
            elif k in INSTANCE_COLUMNS:
                instance_columns.append(k)
            else:
                cluster_columns.append(k)

        def apply_dim(value: str, nodes: str) -> str:
            return f'[dim]{value}[/]' if nodes == '-' else value

        columns, names = [], []
        last_cluster = None
        for item in items:
            name = f'[bold bright_blue]{item["name"]}[/]'
            cluster_values = [item[k] for k in cluster_columns]
            gpu_values = [apply_dim(item[k], item['nodes']) for k in gpu_columns]
            instance_values = [apply_dim(item[k], item['nodes']) for k in instance_columns]
            all_instance_values = SEP + gpu_values + SEP + instance_values
            if name != last_cluster:
                names.append(name)
                columns.append(tuple(cluster_values + all_instance_values))
                last_cluster = name
            else:
                names.append('')
                columns.append(tuple([''] * len(cluster_columns) + all_instance_values))
        column_names = cluster_columns + SEP_HEADER + gpu_columns + SEP_HEADER + instance_columns
        return create_display_table(names, columns, column_names, 'NAME')


@dataclass
class KubeClusterDisplayItem(MCLIDisplayItem):
    id: Optional[str]
    name: str
    provider: str
    context: str
    namespace: str
    gpu_types_and_nums: Dict[str, List[int]]


@cli_error_handler('mcli get clusters')
def get_clusters(
    output: OutputDisplay = OutputDisplay.TABLE,
    include_ids: bool = False,
    **kwargs,
) -> int:
    del kwargs

    clusters = api_get_cluster()
    display = ClusterDisplay(clusters, include_ids=include_ids)
    display.print(output)

    return 0
