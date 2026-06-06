import click
from pathlib import Path
import os
from collections.abc import Iterator
from pathlib import Path

from dev_agent_cli import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="dev-agent")
def main() -> None:
    """Development CLI entry point."""


@main.command()
@click.argument("name", default="world", required=False)
def hello(name: str) -> None:
    """Print a greeting."""
    click.echo(f"Hello, {name}!")

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="dev-agent")
def main() -> None:
    """Development CLI entry point."""


@main.command()
@click.argument("name", default="world", required=False)
def hello(name: str) -> None:
    """Print a greeting."""
    click.echo(f"Hello, {name}!")


DEFAULT_IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    ".direnv",
}
@main.command()
@click.argument(
    "path",
    default=".",
    required=False,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        path_type=Path,
    ),
)
@click.option(
    "--ignore",
    "ignored_dirs",
    multiple=True,
    help="Directory name to ignore. Can be used multiple times.",
)
@click.option(
    "--no-default-ignore",
    is_flag=True,
    help="Do not ignore the default directories.",
)
def index(
    path: Path,
    ignored_dirs: tuple[str, ...],
    no_default_ignore: bool,
) -> None:
    """Index a project directory."""
    root = path.resolve()

    ignore_dirs = set(ignored_dirs)

    if not no_default_ignore:
        ignore_dirs.update(DEFAULT_IGNORED_DIRS)

    click.echo(f"Indexing directory: {root}")

    if ignore_dirs:
        click.echo(f"Ignoring directories: {', '.join(sorted(ignore_dirs))}")

    indexed_count = 0

    for file_path in iter_project_files(root, ignore_dirs):
        click.echo(file_path.relative_to(root))
        indexed_count += 1

    click.echo(f"Indexed {indexed_count} files.")


def iter_project_files(root: Path, ignored_dirs: set[str]) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in ignored_dirs
        ]

        current_dir = Path(dirpath)

        for filename in filenames:
            yield current_dir / filename


def should_ignore(path: Path, ignored_dirs: set[str]) -> bool:
    return any(part in ignored_dirs for part in path.parts)