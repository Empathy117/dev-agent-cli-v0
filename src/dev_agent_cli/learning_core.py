from collections.abc import Iterable
from pathlib import Path


def backend_name() -> str:
    """Return the active implementation used by the Learning Core facade."""
    native_core()
    return "c++/cpython-extension"


def scan_project_files(root: Path, ignored_dirs: Iterable[str]) -> list[Path]:
    """Scan project files through the native Learning Core implementation."""
    relative_paths = native_core().scan_project_files(
        str(root),
        tuple(sorted(ignored_dirs)),
    )

    return [Path(relative_path) for relative_path in relative_paths]


def native_core():
    try:
        from dev_agent_cli import _learning_core
    except ImportError as error:
        message = (
            "Learning Core native extension is not built. "
            "Run through the nix-direnv shell with `dev-agent ...`, or run "
            "`python setup.py build_ext --inplace` first."
        )
        raise RuntimeError(message) from error

    return _learning_core
