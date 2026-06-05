import click
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
def index(path: Path) -> None:
    """Index a project directory."""
    root = path.resolve()

    click.echo(f"Indexing directory: {root}")

    indexed_count = 0

    for file_path in iter_project_files(root):
        click.echo(file_path.relative_to(root))
        indexed_count += 1

    click.echo(f"Indexed {indexed_count} files.")


def iter_project_files(root: Path):
    for file_path in root.rglob("*"):
        if should_ignore(file_path):
            continue

        if file_path.is_file():
            yield file_path


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)