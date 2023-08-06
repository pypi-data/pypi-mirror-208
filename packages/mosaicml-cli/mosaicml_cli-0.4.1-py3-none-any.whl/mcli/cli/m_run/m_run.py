""" mcli run Entrypoint """
import argparse
import logging
import textwrap
from http import HTTPStatus
from typing import Optional

from mcli.api.exceptions import MAPIException, cli_error_handler
from mcli.api.runs import create_run, delete_runs
from mcli.api.runs.api_watch_run import EpilogSpinner as CloudEpilogSpinner
from mcli.config import MCLIConfig
from mcli.models.run_config import VALID_OPTIMIZATION_LEVELS
from mcli.sdk import Run, RunConfig, follow_run_logs, get_run, start_run, wait_for_run_status
from mcli.utils.utils_epilog import CommonLog
from mcli.utils.utils_logging import INFO, OK
from mcli.utils.utils_run_status import RunStatus
from mcli.utils.utils_spinner import console_status

logger = logging.getLogger(__name__)


def print_help(**kwargs) -> int:
    del kwargs
    mock_parser = argparse.ArgumentParser()
    _configure_parser(mock_parser)
    mock_parser.print_help()
    return 1


def follow_run(run: Run) -> int:
    final_config = run.config
    last_status: Optional[RunStatus] = None

    with CloudEpilogSpinner(run, RunStatus.RUNNING) as watcher:
        run = watcher.follow()
        last_status = run.status

    # Wait timed out
    common_log = CommonLog(logger)
    if last_status is None:
        common_log.log_timeout()
        return 0
    elif last_status == RunStatus.FAILED_PULL:
        common_log.log_pod_failed_pull(run.name, final_config.image)
        with console_status('Deleting failed run...'):
            delete_runs([run])
        return 1
    elif last_status == RunStatus.FAILED:
        common_log.log_pod_failed(run.name)
        return 1
    elif last_status.before(RunStatus.RUNNING):
        common_log.log_unknown_did_not_start()
        logger.debug(last_status)
        return 1

    logger.info(f'{OK} Run [cyan]{run.name}[/] started')
    logger.info(f'{INFO} Following run logs. Press Ctrl+C to quit.\n')

    end = ''
    for line in follow_run_logs(run, rank=0):
        print(line, end=end)
    if not end:
        print('')

    wait_for_run_status(run, status=RunStatus.COMPLETED, timeout=10)

    return 0


def finish_run(run: Run, follow: bool, restarted: bool = False) -> int:
    if not follow:
        log_cmd = f'mcli logs {run.name}'
        message = f"""
        {OK} Run [cyan]{run.name}[/] {'re' if restarted else ''}submitted.

        To see the run\'s status, use:

        [bold]mcli get runs[/]

        To see the run\'s logs, use:

        [bold]{log_cmd}[/]
        """
        logger.info(textwrap.dedent(message).strip())
        return 0
    else:
        return follow_run(run)


# pylint: disable-next=too-many-statements
@cli_error_handler('mcli run')
def run_entrypoint(
    file: Optional[str] = None,
    restart_run: Optional[str] = None,
    clone: Optional[str] = None,
    follow: bool = True,
    override_cluster: Optional[str] = None,
    override_gpu_type: Optional[str] = None,
    override_gpu_num: Optional[int] = None,
    override_image: Optional[str] = None,
    override_name: Optional[str] = None,
    override_optimization_level: Optional[int] = None,
    override_priority: Optional[str] = None,
    override_nodes: Optional[int] = None,
    override_instance: Optional[str] = None,
    **kwargs,
) -> int:
    del kwargs

    if file:
        run_config = RunConfig.from_file(path=file)
    elif clone:
        run = get_run(clone)
        if run.submitted_config is None:
            raise MAPIException(HTTPStatus.NOT_FOUND, f"Could not retrieve configuration from run {clone}")
        run_config = run.submitted_config
    elif restart_run:
        with console_status('Restarting run...'):
            run = start_run(restart_run, timeout=None)

        return finish_run(run, follow, restarted=True)

    else:
        return print_help()

    # command line overrides
    # only supports basic format for now and not structured params
    if override_cluster is not None:
        run_config.compute['cluster'] = override_cluster

    if override_gpu_type is not None:
        run_config.compute['gpu_type'] = override_gpu_type

    if override_gpu_num is not None:
        run_config.compute['gpus'] = override_gpu_num

    if override_image is not None:
        run_config.image = override_image

    if override_name is not None:
        run_config.name = override_name

    if override_optimization_level is not None:
        run_config.optimization_level = override_optimization_level

    if override_priority is not None:
        run_config.scheduling['priority'] = override_priority

    if override_instance is not None:
        run_config.compute['instance'] = override_instance

    if override_nodes is not None:
        run_config.compute['nodes'] = override_nodes

    with console_status('Submitting run...'):
        run = create_run(run=run_config, timeout=None)

    return finish_run(run, follow)


def add_run_argparser(subparser: argparse._SubParsersAction) -> None:
    run_parser: argparse.ArgumentParser = subparser.add_parser(
        'run',
        aliases=['r'],
        help='Launch a run in the MosaicML platform',
    )
    run_parser.set_defaults(func=run_entrypoint)
    _configure_parser(run_parser)


def _configure_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        '-f',
        '--file',
        dest='file',
        help='File from which to load arguments.',
    )

    parser.add_argument(
        '-r',
        '--restart',
        dest='restart_run',
        help='Previously stopped run to start again',
    )

    parser.add_argument(
        '--clone',
        dest='clone',
        help='Copy the run config from an existing run',
    )

    parser.add_argument(
        '--priority',
        dest='override_priority',
        help='Priority level at which runs should be submitted. For low priority runs, '
        'use "low" and for high priority runs use "high" '
        '(default None)',
    )

    parser.add_argument(
        '--no-follow',
        action='store_false',
        dest='follow',
        default=False,
        help='Do not automatically try to follow the run\'s logs. This is the default behavior',
    )

    parser.add_argument('--follow',
                        action='store_true',
                        dest='follow',
                        default=False,
                        help='Follow the logs of an in-progress run.')

    parser.add_argument(
        '--cluster',
        '--platform',
        dest='override_cluster',
        help='Optional override for MCLI cluster',
    )

    parser.add_argument(
        '--gpu-type',
        dest='override_gpu_type',
        help='Optional override for GPU type. Valid GPU type depend on'
        ' the cluster and GPU number requested',
    )

    parser.add_argument(
        '--gpus',
        type=int,
        dest='override_gpu_num',
        help='Optional override for number of GPUs. Valid GPU numbers '
        'depend on the cluster and GPU type',
    )

    parser.add_argument(
        '--image',
        dest='override_image',
        help='Optional override for docker image',
    )

    parser.add_argument(
        '--name',
        '--run-name',
        dest='override_name',
        help='Optional override for run name',
    )

    parser.add_argument(
        '--nodes',
        type=int,
        dest='override_nodes',
        help='Optional override for number of nodes. '
        'Valid node numbers depend on the cluster and instance type',
    )

    parser.add_argument(
        '--instance',
        dest='override_instance',
        help='Optional override for instance type',
    )

    conf = MCLIConfig.load_config(safe=True)
    if conf.internal:
        parser.add_argument(
            '-o',
            '--optimization_level',
            dest='override_optimization_level',
            choices=VALID_OPTIMIZATION_LEVELS,
            type=int,
            help='Optimization level for auto-optimization agent. '
            '0 to disable, 1 for safe system-level speedups, 2 for optimal speed at same accuracy, '
            '3 for optimal accuracy at same speed',
        )
