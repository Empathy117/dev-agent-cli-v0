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

## Development

```sh
pytest
ruff check .
ruff format .
```
