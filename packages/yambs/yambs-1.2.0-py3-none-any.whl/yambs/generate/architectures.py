"""
A module for generating architecture-related files.
"""

# built-in
from pathlib import Path

# third-party
from jinja2 import Environment

# internal
from yambs.config import Config
from yambs.generate.common import render_template


def generate(jinja: Environment, ninja_root: Path, config: Config) -> None:
    """Generate architecture-related ninja files."""

    for name, data in config.data["architectures"].items():  # type: ignore
        architectures_root = ninja_root.joinpath("architectures", name)
        architectures_root.mkdir(parents=True, exist_ok=True)

        render_template(
            jinja,
            architectures_root,
            "architecture.ninja",
            data,  # type: ignore
        )
