"""
A module for generating board-related files.
"""

# built-in
from os import linesep
from pathlib import Path
from typing import Any, Dict, Set, TextIO, Tuple

# third-party
from jinja2 import Environment
from vcorelib.paths import rel

# internal
from yambs.config import Config
from yambs.generate.common import render_template


def write_source_line(stream: TextIO, source: Path, base: Path) -> None:
    """Write a ninja configuration line for a source file."""

    source = source.relative_to(base)
    stream.write(
        f"build $build_dir/{source.with_suffix('.o')}: cc $src_dir/{source}"
        + linesep
    )


def write_continuation(stream: TextIO, offset: str) -> None:
    """Write a line continuation."""
    stream.write(" $" + linesep + offset)


def write_link_line(
    stream: TextIO, source: Path, all_srcs: Set[Path], base: Path
) -> None:
    """
    Write a ninja configuration line for an application requiring linking.
    """

    source = source.relative_to(base)

    elf = f"$build_dir/{source.with_suffix('.elf')}"
    line = f"build {elf}: link "
    offset = " " * len(line)
    stream.write(line + f"$build_dir/{source.with_suffix('.o')}")

    for src in all_srcs:
        write_continuation(stream, offset)
        stream.write(f"$build_dir/{src.relative_to(base).with_suffix('.o')}")
    stream.write(linesep)

    # Add lines for creating binaries.
    bin_path = f"$build_dir/{source.with_suffix('.bin')}"
    stream.write(f"build {bin_path}: bin {elf}" + linesep)

    # Add an objdump target.
    dump_path = f"$build_dir/{source.with_suffix('.dump')}"
    stream.write(f"build {dump_path}: dump {elf}" + linesep + linesep)


def is_source(path: Path) -> bool:
    """Determine if a file is a source file."""

    return path.name.endswith(".c") or path.name.endswith(".cc")


def add_dir(
    stream: TextIO, paths: Set[Path], path: Path, comment: str, base: Path
) -> None:
    """Add a directory to set of paths."""

    print(f"{comment}: checking '{path}' for sources.")
    if path.is_dir():
        stream.write(linesep + f"# {comment}." + linesep)
        for item in path.iterdir():
            if is_source(item):
                write_source_line(stream, item, base)
                paths.add(item)


def create_paths_dict(
    root: Path, board: Dict[str, Any], config: Config
) -> Dict[str, Any]:
    """Create paths based on common pathing conventions."""

    chip = config.data["chips"][board["chip"]]  # type: ignore

    return {
        "Common": root.joinpath("common"),
        "Chip": root.joinpath("chips", board["chip"]),
        "Architecture": root.joinpath(chip["architecture"]),  # type: ignore
        "CPU": root.joinpath(chip["cpu"]),  # type: ignore
        "Board": root.joinpath("boards", board["name"]),
    }


def write_sources(
    stream: TextIO, board: Dict[str, Any], config: Config, src_root: Path
) -> Tuple[Set[Path], Set[Path]]:
    """Write the source-file manifest."""

    # Add regular sources.
    all_srcs: Set[Path] = set()
    for kind, path in create_paths_dict(src_root, board, config).items():
        add_dir(
            stream,
            all_srcs,
            path,
            f"{kind} sources",
            src_root,
        )

    # Add application sources.
    app_srcs: Set[Path] = set()
    for kind, path in create_paths_dict(
        src_root.joinpath("apps"), board, config
    ).items():
        add_dir(
            stream, app_srcs, path, f"{kind} application sources", src_root
        )

    return all_srcs, app_srcs


def write_phony(stream: TextIO, app_srcs: Set[Path], base: Path) -> None:
    """Write the phony target."""

    phonies = [("apps", ".bin"), ("dumps", ".dump")]

    if app_srcs:
        for phony, suffix in phonies:
            srcs = list(app_srcs)
            first = srcs[0].relative_to(base)
            srcs = srcs[1:]

            line = f"build {phony}: phony "
            offset = " " * len(line)
            stream.write(line + f"$build_dir/{first.with_suffix(suffix)}")
            for src in srcs:
                write_continuation(stream, offset)
                src = src.relative_to(base)
                stream.write(f"$build_dir/{src.with_suffix(suffix)}")

            stream.write(linesep)


def generate(jinja: Environment, ninja_root: Path, config: Config) -> None:
    """Generate board-related ninja files."""

    # Render the board manifest and rules file.
    for template in ["all.ninja", "rules.ninja"]:
        render_template(jinja, ninja_root, template, config.data)

    src_root = rel(config.directory("src_root"))

    # Render board top-level files.
    board: Dict[str, Any] = {}
    for board in config.data["boards"]:  # type: ignore
        board_root = ninja_root.joinpath("boards", board["name"])
        board_root.mkdir(parents=True, exist_ok=True)
        render_template(jinja, board_root, "board.ninja", board)

        # Perform source-file discovery.
        with board_root.joinpath("sources.ninja").open("w") as path_fd:
            path_fd.write(f"src_dir = {config.data['src_root']}" + linesep)

            all_srcs, app_srcs = write_sources(
                path_fd, board, config, src_root
            )

        print(
            (
                f"({board['name']}) Found {len(all_srcs)} "
                f"sources and {len(app_srcs)} applications."
            )
        )

        # Write the application manifest.
        with board_root.joinpath("apps.ninja").open("w") as path_fd:
            for app_src in app_srcs:
                write_link_line(path_fd, app_src, all_srcs, src_root)

            # Write the phony target.
            path_fd.write("# A target to build all applications." + linesep)
            write_phony(path_fd, app_srcs, src_root)
