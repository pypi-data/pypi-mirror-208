"""CLI getter for users"""
import functools
import logging
from dataclasses import dataclass
from typing import Generator

from mcli.api.exceptions import cli_error_handler
from mcli.api.users.api_get_users import get_users as api_get_users
from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay

logger = logging.getLogger(__name__)


@dataclass
@functools.total_ordering
class UserOrganization(MCLIDisplayItem):
    organization_id: str
    organization_name: str
    id: str
    name: str
    email: str

    def __lt__(self, other: 'UserOrganization'):
        return f'{self.organization_name}-{self.email}' < f'{other.organization_name}-{other.email}'


class UserDisplay(MCLIGetDisplay):
    """`mcli get users` display class
    """

    def __init__(self, users):
        self.users = sorted(
            [UserOrganization(o.id, o.name, u.id, u.name, u.email) for u in users for o in u.organizations])

    def __iter__(self) -> Generator[UserOrganization, None, None]:
        last_org = None
        for u in self.users:
            org_id = u.organization_id
            if last_org == org_id:
                u.organization_id = ''
                u.organization_name = ''

            yield u

            last_org = org_id

    @property
    def index_label(self) -> str:
        return 'organization_id'


@cli_error_handler('mcli get users')
def get_users(output: OutputDisplay = OutputDisplay.TABLE, **kwargs) -> int:
    del kwargs

    users = api_get_users()
    display = UserDisplay(users)
    display.print(output)

    return 0
