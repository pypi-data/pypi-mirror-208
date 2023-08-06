"""CLI getter for secrets"""
import logging
from dataclasses import dataclass
from typing import Generator, List, Optional, Union

from mcli.api.exceptions import cli_error_handler
from mcli.api.secrets.api_get_secrets import get_secrets
from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay
from mcli.models import Secret, SecretType
from mcli.utils.utils_date import get_human_readable_date
from mcli.utils.utils_spinner import console_status

logger = logging.getLogger(__name__)


@dataclass
class SecretDisplayItem(MCLIDisplayItem):
    id: Optional[str]
    name: str
    type: SecretType
    created_at: str


class SecretDisplay(MCLIGetDisplay):
    """`mcli get secrets` display class
    """

    def __init__(self, secrets: List[Secret], include_ids: bool = False):
        self.secrets = secrets
        self.include_ids = include_ids

    def __iter__(self) -> Generator[SecretDisplayItem, None, None]:
        for secret in self.secrets:
            yield SecretDisplayItem(
                id=secret.id if self.include_ids else None,
                name=secret.name,
                type=secret.secret_type,
                created_at=get_human_readable_date(secret.created_at) if secret.created_at else 'Unknown',
            )


@cli_error_handler('mcli get secrets')
def cli_get_secrets(
    output: OutputDisplay = OutputDisplay.TABLE,
    secret_type: str = "all",
    include_ids: bool = False,
    **kwargs,
) -> int:
    """Get currently configured secrets from the reference cluster

    Args:
        output: Output display type. Defaults to OutputDisplay.TABLE.
        secret_type: Filter for secret type. Defaults to 'all' (no filter).

    Returns:
        0 if call succeeded, else 1
    """
    del kwargs

    with console_status('Retrieving requested secrets...'):
        secret_types: Union[List[str], List[SecretType]]
        if secret_type == 'all':
            secret_types = []
        else:
            secret_types = [secret_type]

        found_secrets = get_secrets(secret_types=secret_types, timeout=None)

    display = SecretDisplay(found_secrets, include_ids=include_ids)
    display.print(output)

    return 0
