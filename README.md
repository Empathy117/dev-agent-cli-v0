# dev-agent-cli

Python Click CLI development environment powered by Nix and nix-direnv.

## Setup

Install `nix-direnv`, then allow the environment once:

```sh
direnv allow
```

The shell provides Python, Click, pytest, ruff, build tooling, and a local
`dev-agent` command wired to the current source tree.

## Usage

Run the CLI directly from the development shell:

```sh
dev-agent --help
dev-agent hello Alice
dev-agent index .
```

The `dev-agent` command is provided by the Nix flake dev shell, so
`pip install -e .` is not required for day-to-day development. The generated
`flake.lock` pins the nixpkgs revision used by the environment.

## Architecture

This project uses a two-layer learning architecture:

```text
Product Layer
  src/dev_agent_cli/cli.py
  src/dev_agent_cli/product/indexing.py

Learning Core
  src/dev_agent_cli/learning_core.py
  src/dev_agent_cli/learning_core.cpp
```

The Product Layer owns CLI behavior, user-facing options, output formatting,
and workflow decisions.

The Learning Core owns the lower-level implementation. The current scanner is a
C++ CPython extension that uses `std::filesystem` to walk directories and the
Python C API to return Python objects.

Useful commands:

```sh
dev-agent core-info
dev-agent index .
```

`dev-agent` automatically runs `python setup.py build_ext --inplace --quiet`
before launching, so the native Learning Core is rebuilt when needed.

## Development

```sh
python setup.py build_ext --inplace
pytest
ruff check .
ruff format .
```
