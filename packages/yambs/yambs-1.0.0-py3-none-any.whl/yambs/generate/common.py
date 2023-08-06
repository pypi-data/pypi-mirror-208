"""
A module containing common generation utilities.
"""

# built-in
from os import linesep
from pathlib import Path
from typing import Any, Dict

# third-party
from jinja2 import Environment

# third-party
from vcorelib import DEFAULT_ENCODING


def render_template(
    jinja: Environment,
    root: Path,
    name: str,
    data: Dict[str, Any],
    out: str = None,
) -> None:
    """Render a single template."""

    if out is None:
        out = name

    with root.joinpath(out).open("w", encoding=DEFAULT_ENCODING) as path_fd:
        path_fd.write(jinja.get_template(f"{name}.j2").render(data))
        path_fd.write(linesep)
