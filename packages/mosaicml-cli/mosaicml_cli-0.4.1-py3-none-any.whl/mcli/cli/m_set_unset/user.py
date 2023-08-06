""" mcli modify user functions """
import argparse
import logging
from typing import Optional

from mcli.config import MESSAGE, MCLIConfig, MCLIConfigError
from mcli.utils.utils_logging import OK

logger = logging.getLogger(__name__)


def modify_user(
    user_id: Optional[str] = None,
    **kwargs,
) -> int:
    """Sets user for admin mode

    Returns:
        0 if succeeded, else 1
    """
    del kwargs

    # Get the current user
    try:
        conf = MCLIConfig.load_config()
    except MCLIConfigError:
        logger.error(MESSAGE.MCLI_NOT_INITIALIZED)
        return 1

    conf.user_id = user_id
    conf.save_config()

    if user_id:
        logger.info(f"{OK} Updated User to {user_id}")
    else:
        logger.info(f"{OK} Removed User")
    return 0


def configure_user_argparser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('user_id')
