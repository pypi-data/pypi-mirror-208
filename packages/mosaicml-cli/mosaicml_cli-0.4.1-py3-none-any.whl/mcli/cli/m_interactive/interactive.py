"""
mcloud interactive
"""

import argparse
import logging
from typing import Optional

from mcli.api.cluster import get_clusters
from mcli.api.exceptions import MintException
from mcli.api.mint import shell
from mcli.api.runs.api_watch_run import EpilogSpinner as CloudEpilogSpinner
from mcli.cli.m_get.display import format_timestamp
from mcli.sdk import Run, RunConfig, RunStatus, create_run, get_runs
from mcli.utils.utils_epilog import CommonLog
from mcli.utils.utils_interactive import choose_one
from mcli.utils.utils_logging import FAIL
from mcli.utils.utils_types import get_hours_type

logger = logging.getLogger(__name__)


def wait_for_run(run: Run) -> bool:
    last_status: Optional[RunStatus] = None
    with CloudEpilogSpinner(run, RunStatus.RUNNING) as watcher:
        run = watcher.follow()
        last_status = run.status

    common_log = CommonLog(logger)
    if last_status is None:
        common_log.log_timeout()
        return False
    elif last_status == RunStatus.RUNNING:
        common_log.log_run_interactive_starting(run.name)
        return True
    elif last_status == RunStatus.FAILED:
        if run.reason == "FailedImagePull":
            common_log.log_pod_failed_pull(run.name, run.config.image)
        else:
            common_log.log_pod_failed(run.name)
        return False
    elif last_status.after(RunStatus.RUNNING):
        common_log.log_connect_run_terminating(last_status.display_name)
        return False

    common_log.log_unknown_did_not_start()
    logger.debug(last_status)
    return False


def interactive(
    name: Optional[str] = None,
    cluster: Optional[str] = None,
    gpu_type: Optional[str] = None,
    gpus: Optional[int] = None,
    hours: Optional[float] = None,
    image: str = 'mosaicml/pytorch',
    rank: int = 0,
    connect: bool = True,
    **kwargs,
) -> int:
    del kwargs

    if not cluster:
        clusters = get_clusters()
        if not clusters:
            raise RuntimeError('No clusters available. Contact your administrators to set one up')
        elif len(clusters) == 1:
            cluster = clusters[0].name
        else:
            values = ", ".join([c.name for c in clusters])
            raise RuntimeError('Multiple clusters available. Please use the --cluster argument to set the '
                               f'cluster to use for interactive. Available clusters: {values}')

    run_config = RunConfig(
        name=name or f'interactive-{(gpu_type or "none").replace("_", "-")}-{gpus or 0}'.lower(),
        image=image,
        command=f'sleep {int(3600 * (hours or 1))}',
        gpu_num=gpus,
        gpu_type=gpu_type,
        cluster=cluster,
        optimization_level=0,
    )

    run = create_run(run_config)
    ready = wait_for_run(run)
    if not ready:
        return 1

    if not connect:
        return 0

    try:
        mint_shell = shell.MintShell(run.name, rank=rank)
        mint_shell.connect()
    except MintException as e:
        logger.error(f'{FAIL} {e}')
        return 1
    return 0


def connect_entrypoint(
    name: Optional[str] = None,
    rank: int = 0,
    latest: bool = False,
    command: Optional[str] = None,
    **kwargs,
):
    del kwargs

    if name:
        runs = get_runs([name])
        if not runs:
            # TODO: could have nice suggestions or latest defaults
            logger.error(f'{FAIL} Unknown run {name}')
            return 1
        run = runs[0]
    else:
        available_runs = get_runs(statuses=[RunStatus.STARTING, RunStatus.RUNNING])
        if not available_runs:
            logger.error(f'{FAIL} No running runs available to connect to')
            return 1
        elif len(available_runs) == 1:
            run = available_runs[0]
        else:
            sorted_runs = sorted(available_runs, key=lambda x: x.created_at, reverse=True)

            if len(available_runs) > 10:
                available_runs = sorted(available_runs, key=lambda x: x.created_at, reverse=True)[:10]

            if latest:
                run = sorted_runs[0]
            else:

                def get_name(r: Run):
                    if r.started_at:
                        details = f'Started at {format_timestamp(r.started_at)}'
                    else:
                        details = 'Not yet started'
                    return f'{r.name} ({details})'

                run = choose_one(
                    'What run would you like to connect to?',
                    options=available_runs,
                    formatter=get_name,
                )

    ready = wait_for_run(run)
    if not ready:
        return 1

    try:
        mint_shell = shell.MintShell(run.name, rank=rank)
        mint_shell.connect(command=command)
    except MintException as e:
        logger.error(f'{FAIL} {e}')
        return 1
    return 0


def interactive_entrypoint(
    name: Optional[str] = None,
    cluster: Optional[str] = None,
    gpu_type: Optional[str] = None,
    gpus: Optional[int] = None,
    hrs: Optional[float] = None,
    hours: Optional[float] = None,
    image: str = 'mosaicml/pytorch',
    connect: bool = True,
    rank: int = 0,
    **kwargs,
) -> int:
    del kwargs

    # Hours can be specified as a positional argument (hrs) or named argument (hours)
    if hours and hrs:
        logger.error(f'{FAIL} The duration of your interactive session was specified twice. '
                     'Please use only the positional argument or --hours. '
                     'See mcli interactive --help for more details.')

    hours = hrs or hours
    if hours is None:
        logger.error(f'{FAIL} Please specify the duration of your interactive session. '
                     'See mcli interactive --help for details.')
        return 1
    return interactive(name, cluster, gpu_type, gpus, hours, image, rank, connect)


# TODO: Move into mcli/cli/m_interactive/m_interactive.py once kube mcli deprecated
def configure_argparser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:

    hrs_grp = parser.add_mutually_exclusive_group()
    hrs_grp.add_argument(
        'hrs',
        metavar='HOURS',
        nargs='?',
        type=get_hours_type(),
        help='Number of hours the interactive session should run',
    )
    hrs_grp.add_argument(
        '--hours',
        nargs='?',
        type=get_hours_type(),
        help='Number of hours the interactive session should run',
    )

    parser.add_argument(
        '--name',
        default=None,
        metavar='NAME',
        type=str,
        help='Name for the interactive session. '
        'Default: "interactive-<gpu type>-<gpu num>"',
    )

    cluster_arguments = parser.add_argument_group('Instance settings')
    cluster_arguments.add_argument('--cluster',
                                   default=None,
                                   metavar='CLUSTER',
                                   help='Cluster where your interactive session should run. If you '
                                   'only have one available, that one will be selected by default. '
                                   'Depending on your cluster, you\'ll have access to different GPU types and counts. '
                                   'See the available combinations above. ')

    cluster_arguments.add_argument(
        '--gpu-type',
        metavar='TYPE',
        help='Type of GPU to use. Valid GPU types depend on the cluster and GPU numbers requested',
    )
    cluster_arguments.add_argument(
        '--gpus',
        type=int,
        metavar='NGPUs',
        help='Number of GPUs to run interactively. Valid GPU numbers depend on the cluster and GPU type',
    )

    parser.add_argument(
        '--image',
        default='mosaicml/pytorch',
        help='Docker image to use',
    )

    parser.add_argument(
        '--no-connect',
        dest='connect',
        action='store_false',
        help='Do not connect to the interactive session immediately',
    )

    parser.add_argument('--rank',
                        metavar='N',
                        default=0,
                        type=int,
                        help='Connect to the specified node rank within the run')
    parser.set_defaults(func=interactive_entrypoint)
    return parser


def add_interactive_argparser(subparser: argparse._SubParsersAction,) -> argparse.ArgumentParser:
    """Adds the get parser to a subparser

    Args:
        subparser: the Subparser to add the Get parser to
    """
    examples = """

Examples:

# Create a 1 hour run to be used for interactive
> mcli interactive --hours 1

# Create a 1 hour run to be used for interactive with custom name and docker image
> mcli interactive --hours 1 --image my-image --name my-run

# Connect to the latest run
> mcli connect

# Connect to the rank 1 node from interactive session my-run-1234
> mcli interactive -r my-run-1234 --rank 1
    """

    interactive_parser: argparse.ArgumentParser = subparser.add_parser(
        'interactive',
        help='Create an interactive session',
        description=('Create an interactive session. '
                     'Once created, you can attach to the session. '),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples,
    )
    get_parser = configure_argparser(parser=interactive_parser)
    return get_parser
