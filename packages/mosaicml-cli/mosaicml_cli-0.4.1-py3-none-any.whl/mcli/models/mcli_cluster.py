""" MCLI Abstraction for Clusters """
from __future__ import annotations

import logging
from dataclasses import dataclass

from mcli.utils.utils_serializable_dataclass import SerializableDataclass

logger = logging.getLogger(__name__)


@dataclass
class Cluster(SerializableDataclass):
    """Configured MCLI cluster relating to specific kubernetes context
    """
    name: str
    kubernetes_context: str
    namespace: str
