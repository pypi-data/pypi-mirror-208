"""
A module for generating toolchain-related files.
"""

# built-in
from pathlib import Path

# third-party
from jinja2 import Environment

# internal
from yambs.config import Config
from yambs.generate.common import render_template


def generate(jinja: Environment, ninja_root: Path, config: Config) -> None:
    """Generate toolchain-related ninja files."""

    for name, data in config.data["toolchains"].items():  # type: ignore
        toolchains_root = ninja_root.joinpath("toolchains", name)
        toolchains_root.mkdir(parents=True, exist_ok=True)

        render_template(
            jinja,
            toolchains_root,
            "toolchain.ninja",
            data,  # type: ignore
        )
