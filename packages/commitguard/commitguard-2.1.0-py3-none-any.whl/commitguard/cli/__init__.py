import argparse
import sys

from commitguard import __version__ as version
from commitguard.cli.activate import install_hooks
from commitguard.cli.check import check_hooks
from commitguard.cli.plugins import (
    add_plugins,
    list_plugins,
    plugins,
    remove_plugins,
)
from commitguard.settings import Mode
from commitguard.terminal import Terminal

DESCRIPTION = "commitguard - Manage git hooks"


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version}",
    )

    subparsers = parser.add_subparsers(dest="command")
    activate_parser = subparsers.add_parser(
        "activate", help="Activate the pre-commit hook."
    )
    activate_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force activation of hook even if a hook already exists",
    )
    activate_parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        choices=[
            str(Mode.PYTHONPATH),
            str(Mode.PIPENV),
            str(Mode.POETRY),
        ],
        help="Mode for loading commitguard during hook execution. Either load "
        "commitguard from the PYTHON_PATH, via pipenv or via poetry.",
    )
    activate_parser.set_defaults(func=install_hooks)

    check_parser = subparsers.add_parser(
        "check", help="Check installed pre-commit hook"
    )
    check_parser.set_defaults(func=check_hooks)

    plugins_parser = subparsers.add_parser(
        "plugins", help="Manage commitguard plugins"
    )
    plugins_parser.set_defaults(func=plugins)

    plugins_subparsers = plugins_parser.add_subparsers(
        dest="subcommand", required=True
    )

    add_plugins_parser = plugins_subparsers.add_parser(
        "add", help="Add plugins."
    )
    add_plugins_parser.set_defaults(plugins_func=add_plugins)
    add_plugins_parser.add_argument("name", nargs="+", help="Plugin(s) to add")

    remove_plugins_parser = plugins_subparsers.add_parser(
        "remove", help="Remove plugins."
    )
    remove_plugins_parser.set_defaults(plugins_func=remove_plugins)
    remove_plugins_parser.add_argument(
        "name", nargs="+", help="Plugin(s) to remove"
    )

    list_plugins_parser = plugins_subparsers.add_parser(
        "list", help="List current used plugins."
    )
    list_plugins_parser.set_defaults(plugins_func=list_plugins)

    args = parser.parse_args()

    if not args.command:
        parser.print_usage()
        sys.exit(1)

    term = Terminal()
    args.func(term, args)


if __name__ == "__main__":
    main()
