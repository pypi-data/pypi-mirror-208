""" mcli connect Entrypoint """
import argparse

from mcli.cli.m_interactive.interactive import connect_entrypoint


def configure_argparser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        'name',
        metavar='RUN',
        default=None,
        nargs='?',
        help='Run name',
    )

    parser.add_argument('--rank',
                        metavar='N',
                        default=0,
                        type=int,
                        help='Connect to the specified node rank within the run')

    parser.add_argument(
        '-l',
        '--latest',
        action='store_true',
        dest='latest',
        default=False,
        help='Connect to the latest run',
    )
    parser.add_argument(
        '--command',
        help='The command to execute in the run. By default you will be dropped into a bash shell',
    )

    parser.set_defaults(func=connect_entrypoint)
    return parser


def add_connect_argparser(subparser: argparse._SubParsersAction,) -> argparse.ArgumentParser:
    """Adds the get parser to a subparser

    Args:
        subparser: the Subparser to add the Get parser to
    """
    examples = """

Examples:

# Connect to an existing run
> mcli connect my-run-1234

# Connect to the rank 1 node from my-run-1234
> mcli connect my-run-1234 --rank 1
    """

    connect_parser: argparse.ArgumentParser = subparser.add_parser(
        'connect',
        help='Create an interactive session that\'s connected to a run',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples,
    )

    get_parser = configure_argparser(parser=connect_parser)
    return get_parser
