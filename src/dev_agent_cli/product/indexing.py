from dataclasses import dataclass
from pathlib import Path

from dev_agent_cli.learning_core import scan_project_files

DEFAULT_IGNORED_DIRS = frozenset(
    {
        ".direnv",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "venv",
    }
)

DEFAULT_IGNORED_FILE_SUFFIXES = (
    ".dll",
    ".dylib",
    ".pyc",
    ".pyd",
    ".so",
)


@dataclass(frozen=True)
class IndexResult:
    root: Path
    ignored_dirs: tuple[str, ...]
    relative_files: tuple[Path, ...]


def index_project(
    path: Path,
    *,
    extra_ignored_dirs: tuple[str, ...] = (),
    use_default_ignored_dirs: bool = True,
) -> IndexResult:
    """Build the product-level index result from the Learning Core output."""
    root = path.resolve()
    ignored_dirs = set(extra_ignored_dirs)

    if use_default_ignored_dirs:
        ignored_dirs.update(DEFAULT_IGNORED_DIRS)

    relative_files = [
        relative_file
        for relative_file in scan_project_files(root, ignored_dirs)
        if relative_file.suffix not in DEFAULT_IGNORED_FILE_SUFFIXES
    ]

    return IndexResult(
        root=root,
        ignored_dirs=tuple(sorted(ignored_dirs)),
        relative_files=tuple(sorted(relative_files)),
    )
