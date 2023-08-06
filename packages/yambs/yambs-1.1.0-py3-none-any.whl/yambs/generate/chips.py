"""
A module for generating chip-related files.
"""

# built-in
from pathlib import Path

# third-party
from jinja2 import Environment

# internal
from yambs.config import Config
from yambs.generate.common import render_template


def generate(jinja: Environment, ninja_root: Path, config: Config) -> None:
    """Generate chip-related ninja files."""

    for name, data in config.data["chips"].items():  # type: ignore
        chips_root = ninja_root.joinpath("chips", name)
        chips_root.mkdir(parents=True, exist_ok=True)

        # Render chip files and linker scripts.
        render_template(
            jinja,
            chips_root,
            "chip.ninja",
            data,  # type: ignore
        )
        render_template(
            jinja,
            chips_root,
            "chip.ld",
            data["linker"],  # type: ignore
        )
