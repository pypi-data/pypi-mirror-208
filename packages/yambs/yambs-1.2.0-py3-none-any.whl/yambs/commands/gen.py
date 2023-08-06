"""
An entry-point for the 'gen' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from pathlib import Path as _Path
from sys import executable

# third-party
from rcmpy.watch import watch
from rcmpy.watch.params import WatchParams
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from yambs import PKG_NAME
from yambs.config import Config
from yambs.generate import generate


def gen_cmd(args: _Namespace) -> int:
    """Execute the gen command."""

    config = Config.decode(args.config, includes_key="includes")

    config.root = args.dir
    config.root.mkdir(parents=True, exist_ok=True)

    generate(config)

    return (
        watch(
            WatchParams(
                args.dir,
                _Path(str(config.data["src_root"])),
                [
                    executable,
                    "-m",
                    PKG_NAME,
                    "-C",
                    str(args.dir),
                    "gen",
                    "-c",
                    str(args.config),
                ],
                False,  # Don't check file contents.
                single_pass=args.single_pass,
            )
        )
        if args.watch
        else 0
    )


def add_gen_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add gen-command arguments to its parser."""

    parser.add_argument(
        "-c",
        "--config",
        type=_Path,
        default=f"{PKG_NAME}.yaml",
        help=(
            "the path to the top-level configuration "
            "file (default: '%(default)s')"
        ),
    )
    parser.add_argument(
        "-i",
        "--single-pass",
        action="store_true",
        help="only run a single watch iteration",
    )
    parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="whether or not to continue watching for source tree changes",
    )

    return gen_cmd
