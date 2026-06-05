# dev-agent-cli

Python Click CLI development environment powered by Nix and nix-direnv.

## Setup

Install `nix-direnv`, then allow the environment once:

```sh
direnv allow
```

The shell provides Python, Click, pytest, ruff, and build tooling.

## Usage

Run the CLI directly:

```sh
python -m dev_agent_cli --help
python -m dev_agent_cli hello Alice
```

Install the local console script in editable mode when needed:

```sh
pip install -e .
dev-agent --help
```

## Development

```sh
pytest
ruff check .
ruff format .
```
