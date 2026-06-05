from click.testing import CliRunner

from dev_agent_cli.cli import main


def test_hello_default() -> None:
    result = CliRunner().invoke(main, ["hello"])

    assert result.exit_code == 0
    assert result.output == "Hello, world!\n"


def test_hello_name() -> None:
    result = CliRunner().invoke(main, ["hello", "Alice"])

    assert result.exit_code == 0
    assert result.output == "Hello, Alice!\n"
