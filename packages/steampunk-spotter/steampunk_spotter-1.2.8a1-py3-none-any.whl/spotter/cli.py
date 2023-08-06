"""Provide main CLI parser."""

import argparse
import sys
from pathlib import Path
from typing import Dict, Union, Sequence, Optional, Any, NoReturn

import colorama

from spotter.api import ApiClient
from spotter.commands import login, logout, register, scan, suggest, set_policies, clear_policies
from spotter.storage import Storage
from spotter.utils import get_current_cli_version, validate_url


class ArgParser(argparse.ArgumentParser):
    """An argument parser that displays help on error."""

    def error(self, message: str) -> NoReturn:
        """
        Overridden the original error method.

        :param message: Error message
        """
        print(f"error: {message}\n", file=sys.stderr)
        self.print_help()
        sys.exit(2)

    def add_subparsers(self, **kwargs: Dict[str, Any]) -> argparse._SubParsersAction:  # type: ignore
        """Overridden the original add_subparsers method (workaround for http://bugs.python.org/issue9253)."""
        subparsers = super().add_subparsers()
        subparsers.required = True
        subparsers.dest = "command"
        self._positionals.title = "commands"  # pylint: disable=protected-access
        return subparsers


def create_parser() -> ArgParser:
    """
    Create argument parser for CLI.

    :return: Parser as argparse.ArgumentParser object
    """
    parser = ArgParser(
        description="Steampunk Spotter - Ansible Playbook Scanning Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="additional information:\n"
               "  You will need Steampunk Spotter account to be able to use the CLI.\n"
               "  Create one with spotter register command or at https://spotter.steampunk.si/.\n\n"
               "  To log in to Steampunk Spotter, you should provide your API token or username and password:\n"
               "    - using spotter login command;\n"
               "    - via --api-token/-t optional argument;\n"
               "    - by setting SPOTTER_API_TOKEN environment variable;\n"
               "    - via --username/-u and --password/-p global optional arguments;\n"
               "    - by setting SPOTTER_USERNAME and SPOTTER_PASSWORD environment variables.\n\n"
               "  What do you think about Spotter? Share your thoughts at "
               "https://spotter.steampunk.si/feedback.\n"
               "  Need more help or having other questions? Contact us at https://steampunk.si/contact/."
    )

    parser.add_argument(
        "--version", "-v", action=PrintCurrentVersionAction, nargs=0,
        help="Display the version of Steampunk Spotter CLI"
    )
    parser.add_argument(
        "--endpoint", "-e", type=validate_url,
        help=f"Steampunk Spotter API endpoint (instead of default {ApiClient.DEFAULT_ENDPOINT})"
    )
    parser.add_argument(
        "--storage-path", "-s", type=lambda p: Path(p).absolute(),
        help=f"Storage folder location (instead of default {Storage.DEFAULT_PATH})"
    )
    parser.add_argument(
        "--api-token", "-t", type=str, help="Steampunk Spotter API token"
    )
    parser.add_argument(
        "--username", "-u", type=str, help="Steampunk Spotter username"
    )
    parser.add_argument(
        "--password", "-p", type=str, help="Steampunk Spotter password"
    )
    parser.add_argument(
        "--no-colors", action="store_true", help="Disable output colors"
    )

    subparsers = parser.add_subparsers()
    subparsers_metavar = ""
    cmds = [
        (register.__name__.rsplit(".", maxsplit=1)[-1], register),
        (login.__name__.rsplit(".", maxsplit=1)[-1], login),
        (logout.__name__.rsplit(".", maxsplit=1)[-1], logout),
        (scan.__name__.rsplit(".", maxsplit=1)[-1], scan),
        (suggest.__name__.rsplit(".", maxsplit=1)[-1], suggest),
        (set_policies.__name__.rsplit(".", maxsplit=1)[-1], set_policies),
        (clear_policies.__name__.rsplit(".", maxsplit=1)[-1], clear_policies)
    ]
    for command_name, module in cmds:
        # FIXME: Remove this if we decide that suggest command can be used standalone
        if command_name != "suggest":
            subparsers_metavar += f"{command_name.replace('_', '-')},"
        module.add_parser(subparsers)

    subparsers.metavar = f"{{{subparsers_metavar.rstrip(',')}}}"
    return parser


class PrintCurrentVersionAction(argparse.Action):
    """An argument parser action for displaying current Python package version."""

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                 values: Union[str, Sequence[str], None], option_string: Optional[str] = None) -> NoReturn:
        """
        Overridden the original __call__ method for argparse.Action.

        :param parser: ArgumentParser object
        :param namespace: Namespace object
        :param values: Command-line arguments
        :param option_string: Option string used to invoke this action.
        """
        print(get_current_cli_version())
        sys.exit(0)


def main() -> None:
    """Create main CLI parser and parse arguments."""
    colorama.init(autoreset=True)
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
