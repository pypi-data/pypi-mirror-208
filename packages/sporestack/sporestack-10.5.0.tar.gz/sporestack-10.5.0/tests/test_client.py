from sporestack.api_client import APIClient
from sporestack.client import Client, Server, Token


def test_client() -> None:
    client = Client()
    assert isinstance(client.api_client, APIClient)


def test_server() -> None:
    server = Server(machine_id="foobar")
    assert isinstance(server.api_client, APIClient)


def test_token() -> None:
    token = Token()
    assert token.token.startswith("ss_t_")
    assert isinstance(token.api_client, APIClient)
