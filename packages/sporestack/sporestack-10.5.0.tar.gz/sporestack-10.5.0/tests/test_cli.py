import pytest
import typer
from _pytest.monkeypatch import MonkeyPatch
from sporestack import cli
from sporestack.api_client import TOR_ENDPOINT
from typer.testing import CliRunner

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(cli.cli, ["version"])
    assert "." in result.output
    assert result.exit_code == 0


def test_get_api_endpoint(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("SPORESTACK_ENDPOINT", raising=False)
    monkeypatch.delenv("SPORESTACK_USE_TOR_ENDPOINT", raising=False)
    assert cli.get_api_endpoint() == "https://api.sporestack.com"
    monkeypatch.setenv("SPORESTACK_USE_TOR_ENDPOINT", "1")
    assert ".onion" in cli.get_api_endpoint()
    monkeypatch.delenv("SPORESTACK_USE_TOR_ENDPOINT")
    monkeypatch.setenv("SPORESTACK_ENDPOINT", "oog.boog")
    assert cli.get_api_endpoint() == "oog.boog"


def test_cli_api_endpoint(monkeypatch: MonkeyPatch) -> None:
    # So tests pass locally, even if these are set.
    monkeypatch.delenv("SPORESTACK_ENDPOINT", raising=False)
    monkeypatch.delenv("SPORESTACK_USE_TOR_ENDPOINT", raising=False)
    monkeypatch.delenv("TOR_PROXY", raising=False)
    result = runner.invoke(cli.cli, ["api-endpoint"])
    assert result.output == "https://api.sporestack.com" + "\n"
    assert result.exit_code == 0

    monkeypatch.setenv("SPORESTACK_USE_TOR_ENDPOINT", "1")
    result = runner.invoke(cli.cli, ["api-endpoint"])
    assert result.output == TOR_ENDPOINT + " using socks5://127.0.0.1:9050\n"
    assert result.exit_code == 0

    monkeypatch.setenv("TOR_PROXY", "socks5://127.0.0.1:1337")
    result = runner.invoke(cli.cli, ["api-endpoint"])
    assert result.output == TOR_ENDPOINT + " using socks5://127.0.0.1:1337\n"
    assert result.exit_code == 0


def test_get_machine_id() -> None:
    assert cli._get_machine_id("machine_id", "", "token") == "machine_id"

    # machine_id and hostname set
    with pytest.raises(typer.Exit):
        cli._get_machine_id("machine_id", "hostname", "token")

    # Neither is set
    with pytest.raises(typer.Exit):
        cli._get_machine_id("", "", "token")
