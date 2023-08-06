""" mcli stop Entrypoint """
import argparse
import logging
from typing import List, Optional

from mcli.api.exceptions import cli_error_handler
from mcli.cli.common.run_filters import configure_submission_filter_argparser, get_runs_with_filters
from mcli.cli.m_delete.delete import confirm_run_update
from mcli.sdk import stop_runs
from mcli.utils.utils_logging import FAIL, OK, WARN
from mcli.utils.utils_run_status import RunStatus
from mcli.utils.utils_spinner import console_status

logger = logging.getLogger(__name__)


def stop_entrypoint(parser, **kwargs) -> int:
    del kwargs
    parser.print_help()
    return 0


@cli_error_handler('mcli stop run')
def stop_run(
    name_filter: Optional[List[str]] = None,
    cluster_filter: Optional[List[str]] = None,
    before_filter: Optional[str] = None,
    after_filter: Optional[str] = None,
    gpu_type_filter: Optional[List[str]] = None,
    gpu_num_filter: Optional[List[int]] = None,
    status_filter: Optional[List[RunStatus]] = None,
    stop_all: bool = False,
    latest: bool = False,
    # TODO: after implementing mcli resume, force should default true. In its current
    # state, the user has no way of un-doing `stop runs`, so ask for confirmation first
    force: bool = False,
    **kwargs,
) -> int:
    del kwargs

    runs = get_runs_with_filters(
        name_filter,
        cluster_filter,
        before_filter,
        after_filter,
        gpu_type_filter,
        gpu_num_filter,
        status_filter,
        latest,
        stop_all,
    )

    if not runs:
        extra = '' if stop_all else ' matching the specified criteria'
        logger.error(f'{WARN} No runs found{extra}.')
        return 1

    # skip runs that have already been stopped or don't need to be stopped
    filtered_runs = [r for r in runs if r.status <= RunStatus.STOPPING]

    skipped_runs = len(runs) - len(filtered_runs)
    if not filtered_runs:
        if skipped_runs == 1:
            logger.error(f'{WARN} This run has already been stopped or has already finished')
        else:
            logger.error(f'{WARN} These runs have already been stopped or have already finished')
        return 1
    elif skipped_runs == 1:
        logger.error(f'{WARN} 1 run has already been stopped or has already finished. '
                     'Skipping stop request for this run')
    elif skipped_runs:
        logger.error(f'{WARN} {skipped_runs} runs already been stopped or have already finished. '
                     'Skipping stop request for these runs')

    if not force and not confirm_run_update(filtered_runs, 'stop'):
        logger.error(f'{FAIL} Canceling stop runs')
        return 1

    with console_status('Stopping runs...'):
        stop_runs(filtered_runs)

    logger.info(f'{OK} Stopped runs')
    return 0


def add_stop_parser(subparser: argparse._SubParsersAction):
    """Add the parser for stop runs
    """

    stop_parser: argparse.ArgumentParser = subparser.add_parser(
        'stop',
        help='Stop objects created with mcli',
    )
    stop_parser.set_defaults(func=stop_entrypoint, parser=stop_parser)

    subparsers = stop_parser.add_subparsers(
        title='MCLI Objects',
        description='The table below shows the objects that you can stop',
        help='DESCRIPTION',
        metavar='OBJECT',
    )

    stop_run_parser = subparsers.add_parser(
        'run',
        aliases=['runs'],
        help='Stop runs',
    )
    stop_run_parser.set_defaults(func=stop_run)
    configure_submission_filter_argparser('stop', stop_run_parser)

    stop_run_parser.add_argument('-y',
                                 '--force',
                                 dest='force',
                                 action='store_true',
                                 help='Skip confirmation dialog before stopping runs')
    return stop_parser
