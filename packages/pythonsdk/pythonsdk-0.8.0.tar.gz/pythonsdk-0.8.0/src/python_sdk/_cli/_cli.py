import argparse
import shutil
import sys

from python_sdk._cli import _fmt
from python_sdk._cli import _version

_CLI_DEPENDENCIES_INSTALLED: bool = all([shutil.which("black"), shutil.which("isort")])


def app() -> None:
    if not _CLI_DEPENDENCIES_INSTALLED:
        print(
            "CLI dependencies are not installed. "
            "Please run `pip install pythonsdk[cli]` to unlock this functionality.",
            file=sys.stderr,
        )
        sys.exit(1)

    args = _parser().parse_args()

    if args.command == "fmt":
        _fmt.fmt(target=args.target, check=args.check)
    elif args.command == "version":
        _version.version()
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python-sdk", description="Python SDK CLI.")
    subparsers = parser.add_subparsers(title="Commands", dest="command")
    _fmt_parser(subparsers=subparsers)
    _version_parser(subparsers=subparsers)
    return parser


def _fmt_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(name="fmt", description="Format the codebase.")
    parser.add_argument("--check", action="store_true", default=False)
    parser.add_argument("target", metavar="TARGET", nargs="?", default=".", type=str)
    return parser


def _version_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    return subparsers.add_parser(name="version", description="Print the current python-sdk version.")
