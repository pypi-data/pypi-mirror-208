"""
A module for generating templated outputs.
"""

# third-party
from datazen.templates import environment
from jinja2 import FileSystemLoader
from vcorelib.paths import resource

# internal
from yambs import PKG_NAME
from yambs.config import Config
from yambs.generate.architectures import generate as generate_architectures
from yambs.generate.boards import generate as generate_boards
from yambs.generate.chips import generate as generate_chips
from yambs.generate.common import render_template
from yambs.generate.toolchains import generate as generate_toolchains


def generate(config: Config) -> None:
    """Generate ninja files."""

    templates_dir = resource("templates", package=PKG_NAME)
    assert templates_dir is not None

    jinja = environment(
        loader=FileSystemLoader([templates_dir], followlinks=True)
    )

    # Render the top-level configuration. This is the only file that's
    # generated into the root directory.
    render_template(jinja, config.root, "build.ninja", config.data)

    ninja_root = config.directory("ninja_out")

    # Generate all other files.
    for gen in [
        generate_boards,
        generate_chips,
        generate_toolchains,
        generate_architectures,
    ]:
        gen(jinja, ninja_root, config)
