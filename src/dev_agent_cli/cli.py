from pathlib import Path

import click

from dev_agent_cli import __version__
from dev_agent_cli.learning_core import backend_name
from dev_agent_cli.product.indexing import index_project


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="dev-agent")
def main() -> None:
    """Development CLI entry point."""


@main.command()
@click.argument("name", default="world", required=False)
def hello(name: str) -> None:
    """Print a greeting."""
    click.echo(f"Hello, {name}!")


@main.command("core-info")
def core_info() -> None:
    """Show which Learning Core backend is active."""
    click.echo(f"Learning Core backend: {backend_name()}")


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
    result = index_project(
        path,
        extra_ignored_dirs=ignored_dirs,
        use_default_ignored_dirs=not no_default_ignore,
    )

    click.echo(f"Indexing directory: {result.root}")

    if result.ignored_dirs:
        click.echo(f"Ignoring directories: {', '.join(result.ignored_dirs)}")

    for relative_path in result.relative_files:
        click.echo(relative_path.as_posix())

    click.echo(f"Indexed {len(result.relative_files)} files.")
