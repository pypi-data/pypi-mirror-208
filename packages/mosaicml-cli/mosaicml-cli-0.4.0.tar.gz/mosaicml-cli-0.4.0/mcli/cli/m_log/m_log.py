"""mcli logs entrypoint"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from functools import partial
from http import HTTPStatus
from typing import List, Optional, Tuple, Union

from mcli.api.exceptions import MAPIException
from mcli.api.model.inference_deployment import InferenceDeployment
from mcli.api.runs.api_watch_run import EpilogSpinner as CloudEpilogSpinner
from mcli.cli.common.deployment_filters import get_deployments_with_filters
from mcli.cli.common.run_filters import get_runs_with_filters
from mcli.config import MESSAGE, MCLIConfigError
from mcli.sdk import Run, follow_run_logs, get_inference_deployment_logs, get_run_logs
from mcli.utils.utils_cli import SubmissionType
from mcli.utils.utils_epilog import CommonLog
from mcli.utils.utils_logging import FAIL, INFO, err_console
from mcli.utils.utils_run_status import RunStatus

logger = logging.getLogger(__name__)

# pylint: disable-next=invalid-name
RUN_LOG_EXAMPLES = """

Examples:

# View the current logs of an ongoing run
> mcli logs run-1234

# By default, if you don't specify the run name the logs for the latest run will be retrieved
> mcli logs

# View the logs of a specific node in a multi-node run
> mcli logs multinode-run-1234 --rank 1

# Follow the logs for an ongoing run
> mcli logs run-1234 --follow

# View the logs for a failed run
> mcli logs run-1234 --failed
"""

# pylint: disable-next=invalid-name
DEPLOYMENT_LOG_EXAMPLES = """

Examples:

# View the current logs of an ongoing deployment
> mcli get deployment logs deploy-1234

# By default, the logs for the latest deployment will be retrieved
> mcli get deployment logs

# View the logs of a specific restart in a deployment
> mcli get deployment logs deploy-1234 --restart 5
"""


def _get_run_logs(
    run: Run,
    follow: bool,
    rank: Optional[int],
    failed: bool,
) -> Tuple[Optional[str], int]:
    if follow and run.status.before(RunStatus.RUNNING):
        with CloudEpilogSpinner(run, RunStatus.RUNNING) as watcher:
            run = watcher.follow()

    if run.status == RunStatus.FAILED_PULL:
        CommonLog(logger).log_pod_failed_pull(run.name, run.config.image)
        return "", 1
    elif run.status.before(RunStatus.QUEUED, inclusive=True):
        # Pod still waiting to be scheduled. Return
        logger.error(f'{FAIL} Run {run.name} has not been scheduled')
        return "", 1
    elif run.status.before(RunStatus.RUNNING):
        # Pod still not running, probably because follow==False
        logger.error(f'{FAIL} Run has not yet started. You can check the status with `mcli get runs` '
                     'and try again later.')
        return "", 1

    last_line: Optional[str] = None
    end: str = ''
    if follow:
        for line in follow_run_logs(run, rank=rank):
            print(line, end=end)
            if line:
                last_line = line
        return last_line, int(0)
    else:
        log_lines = get_run_logs(run, rank=rank, failed=failed)
        for line in log_lines:
            # When using progress bars we randomly get newlines added. By default,
            # kubernetes does not return empty lines when streaming, which is
            # replicated in `follow_run_logs`. We'll do that here for parity
            if line:
                last_line = line
                print(line, end='')
        return last_line, int(0)


def _get_deployment_logs(deploy: InferenceDeployment, restart) -> Tuple[Optional[str], int]:
    log_lines = get_inference_deployment_logs(deploy, restart=restart)
    last_line: Optional[str] = None
    for line in log_lines:
        # When using progress bars we randomly get newlines added. By default,
        # kubernetes does not return empty lines when streaming, which is
        # replicated in `follow_run_logs`. We'll do that here for parity
        if line:
            last_line = line
            print(line, end='')
    return last_line, 0


def get_with_filters(submission_type: SubmissionType,
                     name: Optional[str] = None,
                     latest: bool = False) -> Union[List[Run], List[InferenceDeployment]]:
    name_filter = [name] if name else None
    if submission_type == SubmissionType.RUN:
        return get_runs_with_filters(name_filter=name_filter, latest=latest)
    else:
        return get_deployments_with_filters(name_filter=name_filter)


# pylint: disable-next=too-many-statements
def get_logs(
    submission_type: SubmissionType,
    submission_name: Optional[str] = None,
    rank: Optional[int] = None,
    restart: Optional[int] = None,
    follow: bool = False,
    failed: bool = False,
    **kwargs,
) -> int:
    del kwargs

    try:
        submission_type_str = submission_type.value.lower()
        with err_console.status(f'Getting {submission_type_str} details...') as spinner:
            if submission_name is None:
                spinner.update(f'No {submission_type_str} name provided. Finding latest {submission_type_str}'
                               f'...')
                submissions = get_with_filters(submission_type, submission_name, latest=True)
                if not submissions:
                    raise MAPIException(status=HTTPStatus.NOT_FOUND, message=f'No {submission_type_str} found')
                logger.info(
                    f'{INFO} No {submission_type_str} name provided. Displaying log of latest {submission_type_str}: '
                    f'[cyan]{submissions[0].name}[/]')
            else:
                submissions = get_with_filters(submission_type, submission_name, latest=True)
                if not submissions:
                    raise MAPIException(status=HTTPStatus.NOT_FOUND,
                                        message=f'Could not find {submission_type_str}: [red]{submission_name}[/]')

        last_line: Optional[str] = None
        #Have to check type to satisfy pyright
        if isinstance(submissions[0], Run):
            last_line, err = _get_run_logs(submissions[0], follow, rank, failed)
            if err == 1:
                return 1
        elif isinstance(submissions[0], InferenceDeployment):
            last_line, err = _get_deployment_logs(submissions[0], restart)
            if err == 1:
                return 1

        # Progress bars are weird. Let's add a final newline so that if the printing
        # ends on an incompleted progress bar, it isn't erased
        if last_line:
            print('', file=sys.stderr)

    except MAPIException as e:
        logger.error(f'{FAIL} {e}')
        return 1
    except RuntimeError as e:
        logger.error(f'{FAIL} {e}')
        return 1
    except MCLIConfigError:
        logger.error(MESSAGE.MCLI_NOT_INITIALIZED)
        return 1
    except BrokenPipeError:
        # This is raised when output is piped to programs like `head`
        # Error handling taken from this example in the python docs:
        # https://docs.python.org/3/library/signal.html#note-on-sigpipe
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())

        return 1

    return 0


def configure_deployments_argparser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.set_defaults(func=partial(get_logs, SubmissionType.DEPLOYMENT))

    parser.add_argument('submission_name',
                        metavar='DEPLOYMENT',
                        help='The name of the inference deployment to fetch logs for.')
    parser.add_argument('--restart',
                        type=int,
                        default=None,
                        help='Which restart to fetch logs for. If not provided, will fetch logs of most recent restart')

    return parser


def configure_runs_argparser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.set_defaults(func=partial(get_logs, SubmissionType.RUN))
    parser.add_argument('submission_name',
                        metavar='RUN',
                        nargs='?',
                        help='The name of the run. If not provided, will return the logs of the latest run')
    rank_grp = parser.add_mutually_exclusive_group()
    rank_grp.add_argument('--rank',
                          type=int,
                          default=None,
                          metavar='N',
                          help='Rank of the node in a multi-node run whose logs you\'d like to view')
    rank_grp.add_argument('--failed',
                          action='store_true',
                          dest='failed',
                          default=False,
                          help='Get the logs of the first failed node rank in a multinode run.')
    follow_grp = parser.add_mutually_exclusive_group()
    follow_grp.add_argument('--no-follow',
                            action='store_false',
                            dest='follow',
                            default=False,
                            help='Do not follow the logs of an in-progress run. '
                            'Simply print any existing logs and exit. This is the default behavior.')
    follow_grp.add_argument('-f',
                            '--follow',
                            action='store_true',
                            dest='follow',
                            default=False,
                            help='Follow the logs of an in-progress run.')

    return parser


def add_log_parser(subparser: argparse._SubParsersAction, submission_type: SubmissionType):
    """Add the parser for retrieving submission logs
    """

    log_parser: argparse.ArgumentParser = subparser.add_parser(
        'logs',
        aliases=['log'],
        help=f'View the logs from a specific {submission_type.value.lower()}',
        description=f'View the logs of an ongoing, completed or failed {submission_type.value.lower()}',
        epilog=RUN_LOG_EXAMPLES if submission_type == SubmissionType.RUN else DEPLOYMENT_LOG_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    log_parser = configure_runs_argparser(
        log_parser) if submission_type == SubmissionType.RUN else configure_deployments_argparser(log_parser)

    return log_parser
