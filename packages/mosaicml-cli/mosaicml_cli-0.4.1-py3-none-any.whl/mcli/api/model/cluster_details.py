""" MCLI Abstraction for Clusters and Utilization """
from __future__ import annotations

import functools
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from dateutil import parser

from mcli.api.exceptions import MAPI_DESERIALIZATION_ERROR
from mcli.api.schema.generic_model import DeserializableModel
from mcli.models.run_config import SchedulingConfig, SchedulingTranslation
from mcli.utils.utils_serializable_dataclass import SerializableDataclass

logger = logging.getLogger(__name__)


def check_response(response: Dict[str, Any], expected: Set[str]) -> None:
    missing = expected - set(response)
    if missing:
        raise MAPI_DESERIALIZATION_ERROR


@dataclass
class ClusterUtilizationByRun:
    """Utilization for a specific run on a cluster
    """

    id: str
    user: str
    run_name: str
    gpu_num: int
    created_at: datetime
    scheduling: SchedulingConfig

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> ClusterUtilizationByRun:
        check_response(response, {'id', 'userName', 'runName', 'gpuNum', 'createdAt'})
        return cls(id=response['id'],
                   user=response['userName'],
                   run_name=response['runName'],
                   gpu_num=response['gpuNum'],
                   created_at=parser.parse(response['createdAt']),
                   scheduling=SchedulingTranslation.from_mapi(response.get('scheduling', {})))


@dataclass
class InstanceUtilization:
    """Utilization on a cluster instance
    """
    cluster_id: str
    gpu_type: str
    gpus_per_node: int
    num_nodes: int
    gpus_used: int
    gpus_available: int
    gpus_total: int

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> InstanceUtilization:
        check_response(response,
                       {'clusterId', 'gpuType', 'gpusPerNode', 'numNodes', 'gpusUsed', 'gpusAvailable', 'gpusTotal'})
        return cls(
            cluster_id=response['clusterId'],
            gpu_type=response['gpuType'],
            gpus_per_node=response['gpusPerNode'],
            num_nodes=response['numNodes'],
            gpus_used=response['gpusUsed'],
            gpus_available=response['gpusAvailable'],
            gpus_total=response['gpusTotal'],
        )


@dataclass
class ClusterUtilization:
    """Utilization on a cluster
    """
    anonymize_users: bool
    cluster_instance_utils: List[InstanceUtilization] = field(default_factory=list)
    active_by_user: List[ClusterUtilizationByRun] = field(default_factory=list)
    queued_by_user: List[ClusterUtilizationByRun] = field(default_factory=list)

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> ClusterUtilization:
        check_response(response, {'clusterInstanceUtils', 'activeByUser', 'queuedByUser', 'anonymizeUsers'})
        return cls(cluster_instance_utils=[
            InstanceUtilization.from_mapi_response(i) for i in response['clusterInstanceUtils']
        ],
                   active_by_user=[ClusterUtilizationByRun.from_mapi_response(i) for i in response['activeByUser']],
                   queued_by_user=[ClusterUtilizationByRun.from_mapi_response(i) for i in response['queuedByUser']],
                   anonymize_users=response['anonymizeUsers'])


@dataclass
class Node:
    """Node on an instance for a cluster
    """
    name: str
    is_alive: bool
    is_schedulable: bool

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> Node:
        check_response(response, {'name', 'isAlive', 'isSchedulable'})
        return cls(name=response['name'], is_alive=response['isAlive'], is_schedulable=response['isSchedulable'])


@dataclass
@functools.total_ordering
class Instance:
    """Instance of a cluster
    """
    name: str
    gpu_type: str
    gpus: int
    nodes: int
    gpu_nums: List[int] = field(default_factory=list)
    node_details: List[Node] = field(default_factory=list)

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> Instance:
        check_response(response, {'name', 'gpusPerNode', 'numNodes', 'gpuType', 'gpuNums', 'nodes'})
        return cls(
            name=response['name'],
            gpu_type=response['gpuType'],
            gpus=response['gpusPerNode'],
            nodes=response['numNodes'],
            gpu_nums=response['gpuNums'],
            node_details=[Node.from_mapi_response(i) for i in response.get('nodes', [])],
        )

    def __lt__(self, other: Instance):
        if self.gpu_type.lower() == 'none':
            return True
        return self.gpu_type < other.gpu_type


def get_provider_name(raw_provider: str):
    raw_provider = raw_provider.upper()

    overrides = {
        'COREWEAVE': 'CoreWeave',
        'MICROK8S': 'MicroK8s',
        'MOSAICML_COLO': 'MosaicML',
        'MINIKUBE': 'Minikube',
    }

    return overrides.get(raw_provider, raw_provider)


@dataclass
@functools.total_ordering
class ClusterDetails(SerializableDataclass, DeserializableModel):
    """Details of a cluster, including instances and utilization
    """

    name: str
    provider: str = 'MosaicML'
    allow_fractional: bool = False
    allow_multinode: bool = False
    cluster_instances: List[Instance] = field(default_factory=list)
    utilization: Optional[ClusterUtilization] = None

    kubernetes_context: str = ''
    namespace: str = ''

    id: Optional[str] = None

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> ClusterDetails:
        check_response(response, {'name'})
        utilization = None if 'utilization' not in response else ClusterUtilization.from_mapi_response(
            response['utilization'])
        return cls(name=response['name'],
                   provider=get_provider_name(response.get('provider', '')),
                   allow_fractional=response.get('allowFractional', False),
                   allow_multinode=response.get('allowMultinode', False),
                   cluster_instances=[Instance.from_mapi_response(i) for i in response.get('allowedInstances', [])],
                   utilization=utilization,
                   id=response.get('id'))

    def __lt__(self, other: ClusterDetails):
        return self.name < other.name
