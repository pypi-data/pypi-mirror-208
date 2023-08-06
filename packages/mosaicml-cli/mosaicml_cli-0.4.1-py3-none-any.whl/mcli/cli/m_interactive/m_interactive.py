""" mcli interactive Entrypoint """
import argparse
import logging
import shlex
import subprocess
from typing import Optional

from mcli.api.exceptions import cli_error_handler
from mcli.cli.m_interactive import kube_config
from mcli.config import MCLIConfig
from mcli.sdk import RunConfig, RunStatus, create_run, get_clusters, get_run, wait_for_run_status
from mcli.utils.utils_interactive import simple_prompt
from mcli.utils.utils_logging import FAIL, INFO, OK, WARN
from mcli.utils.utils_types import get_hours_type

logger = logging.getLogger(__name__)


@cli_error_handler('mcli interactive')
def interactive_entrypoint(
    name: Optional[str] = None,
    cluster: Optional[str] = None,
    gpu_type: Optional[str] = None,
    gpus: Optional[int] = None,
    cpus: int = 1,
    hrs: Optional[float] = None,
    hours: Optional[float] = None,
    image: str = 'mosaicml/pytorch',
    connect: bool = True,
    reconnect: Optional[str] = None,
    rank: int = 0,
    **kwargs,
) -> int:
    # pylint: disable=too-many-statements
    del kwargs

    # Hours can be specified as a positional argument (hrs) or named argument (hours)
    if hours and hrs:
        logger.error(f'{FAIL} The duration of your interactive session was specified twice. '
                     'Please use only the positional argument or --hours. '
                     'See mcli interactive --help for more details.')

    hours = hrs or hours
    if hours is None and reconnect is None:
        logger.error(f'{FAIL} Please specify the duration of your interactive session. '
                     'See mcli interactive --help for details.')
        return 1

    return mcloud_interactive(name, cluster, gpu_type, gpus, cpus, hours, image, rank, connect, reconnect)


# "hacky mcloud" - see interative.py for alpha mcloud interactive
def mcloud_interactive(
    name: Optional[str] = None,
    cluster: Optional[str] = None,
    gpu_type: Optional[str] = None,
    gpus: Optional[int] = None,
    cpus: int = 1,
    hours: Optional[float] = None,
    image: str = 'mosaicml/pytorch',
    rank: int = 0,
    connect: bool = True,
    reconnect: Optional[str] = None,
) -> int:

    if not cluster:
        clusters = get_clusters()
        if not clusters:
            raise RuntimeError('Cluster name must be provided. Use `mcli get clusters` to list available clusters')
        elif len(clusters) == 1:
            cluster = clusters[0].name
        else:
            raise RuntimeError('Multiple clusters available. Please use the --cluster argument to set the '
                               'cluster to use for interactive')

    if reconnect:
        run = get_run(reconnect)
        logger.info(f'{INFO} Attempting to reconnect to session: [cyan]{run.name}[/]')
    else:
        if cpus and cpus != 1:
            logger.info(f'{WARN} Specifying cpus not currently supported. Submitting interactive run with {gpus} gpus')

        config = RunConfig(
            name=name or f'interactive-{(gpu_type or "none").replace("_", "-")}-{gpus or 0}'.lower(),
            image=image,
            command=f'sleep {int(3600 * (hours or 1))}',
            gpu_num=gpus,
            gpu_type=gpu_type,
            cluster=cluster,
            optimization_level=0,
        )

        run = create_run(config)
        logger.info(f'{OK} Interactive session [cyan]{run.name}[/] submitted')

    if connect:
        context = simple_prompt(
            f'Which kube context should be used to connect to the interactive run? [{cluster}]',
            default=cluster,
            mandatory=False,
        )

        kube_config.load_kube_config()

        default_namespace = ''
        for c in kube_config.list_kube_config_contexts()[0]:
            if c.get('name') == context:  # type: ignore
                default_namespace = c.get('context', {}).get('namespace', '')  # type: ignore
                break

        if MCLIConfig.load_config(safe=True).internal:
            default_namespace = 'mosaicml-orchestration'

        namespace = simple_prompt(
            f'Which kube namespace should be used to connect to the interactive run? [{default_namespace}]',
            default=default_namespace,
            mandatory=False,
        )

        pod_id = f"{run.last_attempt_id}-{rank}"
        logger.info(f'{INFO} Waiting for session to start with pod [blue]{pod_id}[/]...')
        logger.info(f'{INFO} Press Ctrl+C to quit and interact with your session manually.')
        run = wait_for_run_status(run, status=RunStatus.RUNNING, timeout=300)

        rank_str = f"node rank [cyan]{rank}[/] of " if rank > 0 else ""
        logger.info(f'{OK} Connecting to {rank_str}interactive session [cyan]{run.name}[/]')

        options = []
        if context:
            options.append(f'--context {shlex.quote(context)}')
        if namespace:
            options.append(f'--namespace {shlex.quote(namespace)}')

        exec_command = f'kubectl exec -it {" ".join(options)} {pod_id} -c main -- /bin/bash'

        with subprocess.Popen(exec_command, shell=True, start_new_session=True) as p:
            return p.wait() == 0

    return 0


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
                                   '--platform',
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
    cluster_arguments.add_argument(
        '--cpus',
        default=1,
        type=int,
        metavar='NCPUs',
        help='Number of CPUs to run interactively. This will only take effect when --gpu-type is set to "none". '
        'Default: %(default)s',
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
    parser.add_argument(
        '-r',
        '--reconnect',
        const='',
        metavar='NAME',
        nargs='?',
        help='Reconnect to an existing interactive session. '
        'You can provide the name of the session you\'d like to reconnect to, or, '
        'if not provided, your most recent one will be used',
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

# Create a 1 hour interactive session
> mcli interactive --hours 1

# Create a 1 hour interactive session with custom name and docker image
> mcli interactive --hours 1 --image my-image --name my-session

# Reconnect to the interactive session my-session-1234
> mcli interactive -r my-session-1234

# Connect to the rank 1 node from interactive session my-session-1234
> mcli interactive -r my-session-1234 --rank 1
    """

    interactive_parser: argparse.ArgumentParser = subparser.add_parser(
        'interactive',
        help='Create an interactive session',
        description=('Create an interactive session. '
                     'Once created, you can attach to the session. '
                     'Interactive sessions are only allowed in pre-specified clusters.'),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples,
    )
    get_parser = configure_argparser(parser=interactive_parser)
    return get_parser
