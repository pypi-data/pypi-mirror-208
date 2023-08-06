import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from . import commands
from .repository import ProjectScenario, RepositoryRemote
from .utils import log, red


def parse_arguments(args: list[str]):
    parser = ArgumentParser(
        description="Push and pull image context to and from numerous workspace.",
        prog="numerous",
    )
    parser.add_argument(
        "-v",
        dest="verbose",
        action="store_true",
        help="Verbose mode. Prints informational messages.",
    )
    parser.add_argument(
        "-vv",
        dest="extra_verbose",
        action="store_true",
        help="Extra verbose mode. Prints debugging information.",
    )

    command_parsers = parser.add_subparsers(
        title="Command", dest="cmd", help="The command to execute.", required=True
    )
    parser_init = command_parsers.add_parser(
        "init", help="Initialize a repository locally."
    )
    parser_init.add_argument("path", help="The path to the repository.", nargs="?")

    parser_checkout = command_parsers.add_parser(
        "checkout", help="Check out a scenario or commit to the repository."
    )
    parser_checkout.add_argument("path", help="The path to the repository.", nargs="?")
    parser_checkout_group = parser_checkout.add_mutually_exclusive_group()
    parser_checkout_group.add_argument(
        "-s", "--scenario", help="The scenario to check out.", type=ProjectScenario
    )
    parser_checkout_group.add_argument(
        "-c", "--commit", help="The commit to check out."
    )

    parser_clone = command_parsers.add_parser(
        "clone", help="Clone a remote repository."
    )
    parser_clone_group = parser_clone.add_mutually_exclusive_group()
    parser_clone_group.add_argument(
        "-s", "--scenario", help="The scenario to clone.", type=ProjectScenario
    )
    parser_clone_group.add_argument("-c", "--commit", help="The commit to clone.")
    parser_clone.add_argument(
        "remote",
        metavar="REMOTE",
        help="The repository remote to clone.",
        type=RepositoryRemote,
    )
    parser_clone.add_argument(
        "path", metavar="PATH", help="The path to clone the repository to.", nargs="?"
    )

    parser_config = command_parsers.add_parser(
        "config", help="Show or update configuration values."
    )
    parser_config.add_argument(
        "path", help="Path to the repository to configure.", nargs="?"
    )
    parser_config.add_argument("--remote", help="The URL of the remote.")
    parser_config.add_argument("--user", help="The user id.")
    parser_config.add_argument("--organization", help="The organization.")
    parser_config.add_argument("--snapshot", help="The repository snapshot.")
    parser_config.add_argument("--scenario", help="The current scenario.")

    parser_log = command_parsers.add_parser("log", help="Show logs for the repository.")
    parser_log.add_argument(
        "-d",
        "--display-mode",
        choices=["git", "table"],
        default="git",
        help="The way each history update from the log is displayed.",
    )
    parser_log.add_argument("path", help="The path to the repository", nargs="?")

    parser_push = command_parsers.add_parser("push", help="Push to the remote.")
    parser_push.add_argument("path", help="The path to the repository.", nargs="?")
    parser_push.add_argument(
        "-c", "--comment", help="The comment for the push commit.", required=True
    )

    parser_build = command_parsers.add_parser("build", help="Build the code the code.")
    parser_build.add_argument("path", help="The path to the repository.", nargs="?")
    parser_build.add_argument("-c", "--commit", help="The commit to build.")
    parser_build.add_argument(
        "-j", "--job", help="The job id of the job to associate the image with."
    )
    parser_build.add_argument("-t", "--tags", help="Extra tags separated by commas.")
    parser_build.add_argument(
        "--timeout",
        help="Specify the build timeout in minutes, with fractional precision (eg. "
        "3.5). It will be rounded to whole seconds.",
        type=float,
    )

    parser_login = command_parsers.add_parser(
        "login", help="Login to the repository remote."
    )
    parser_login.add_argument("path", help="The path to the repository.", nargs="?")

    command_parsers.add_parser(
        "version", help="Get the current version number of this tool."
    )

    return parser.parse_args(args)


def path_or_none(path: str):
    if path is None:
        return None
    else:
        return Path(path)


def set_log_level(verbose: bool, extra_verbose: bool):
    if extra_verbose:
        logging.basicConfig(level=logging.DEBUG)
        log.info("Starting in extra verbose mode")
    elif verbose:
        logging.basicConfig(level=logging.INFO)
        log.info("Starting in verbose mode")


def run_command(ns: Namespace):
    set_log_level(ns.verbose, ns.extra_verbose)
    if ns.cmd == "init":
        commands.command_init(path_or_none(ns.path))
    elif ns.cmd == "clone":
        commands.command_clone(log, ns.scenario, path_or_none(ns.path), ns.remote)
    elif ns.cmd == "log":
        commands.command_log(log, path_or_none(ns.path), ns.display_mode)
    elif ns.cmd == "push":
        commands.command_push(log, path_or_none(ns.path), ns.comment)
    elif ns.cmd == "checkout":
        commands.command_checkout(log, path_or_none(ns.path), ns.scenario, ns.commit)
    elif ns.cmd == "build":
        args = commands.BuildArgs(
            commit=ns.commit,
            tags=[tag.strip() for tag in ns.tags.split(",")] if ns.tags else None,
            timeout=ns.timeout,
        )
        commands.command_build(path_or_none(ns.path), args)
    elif ns.cmd == "config":
        commands.command_config(log, path_or_none(ns.path), ns)
    elif ns.cmd == "version":
        commands.command_version()
    elif ns.cmd == "login":
        commands.command_login(log, path_or_none(ns.path))
    else:
        print(red(f"Invalid {ns.cmd} command given."))


def main():
    ns = parse_arguments(sys.argv[1:])
    run_command(ns)
