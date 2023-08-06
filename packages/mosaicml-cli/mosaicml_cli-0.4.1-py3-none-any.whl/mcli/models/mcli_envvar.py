""" The MCLI Abstraction for Environment Variables """
from dataclasses import dataclass
from typing import Any, Dict, Type

from mcli.utils.utils_serializable_dataclass import SerializableDataclass, T_SerializableDataclass


@dataclass
class MCLIEnvVar(SerializableDataclass):

    key: str
    value: str

    @classmethod
    def from_dict(cls: Type[T_SerializableDataclass], data: Dict[str, Any]) -> T_SerializableDataclass:
        return cls(**data)
