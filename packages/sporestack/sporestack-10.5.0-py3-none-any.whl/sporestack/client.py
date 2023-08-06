from dataclasses import dataclass, field
from typing import List, Union

from . import api
from .api_client import APIClient
from .models import Invoice, TokenInfo
from .utils import random_machine_id, random_token


@dataclass
class Server:
    machine_id: str
    api_client: APIClient = field(default_factory=APIClient)
    token: Union[str, None] = None

    def info(self) -> api.ServerInfo.Response:
        """Returns information about the server."""
        return self.api_client.server_info(self.machine_id)

    def rebuild(self) -> None:
        """Delete all data on the server and reinstall it."""
        self.api_client.server_rebuild(self.machine_id)

    def forget(self) -> None:
        """Forget about the server so it doesn't show up in server listings."""
        self.api_client.server_forget(self.machine_id)

    def delete(self) -> None:
        """Delete the server."""
        self.api_client.server_delete(self.machine_id)

    def start(self) -> None:
        """Powers on the server."""
        self.api_client.server_start(self.machine_id)

    def stop(self) -> None:
        """Powers off the server."""
        self.api_client.server_stop(self.machine_id)

    def autorenew_enable(self) -> None:
        """Enables autorenew on the server."""
        self.api_client.autorenew_enable(self.machine_id)

    def autorenew_disable(self) -> None:
        """Disables autorenew on the server."""
        self.api_client.autorenew_disable(self.machine_id)

    def topup(self, days: int) -> None:
        """
        Renew the server for the amount of days specified, from the token that
        launched the server.
        """
        if self.token is None:
            raise ValueError("token must be set to top up a server!")
        self.api_client.server_topup(
            machine_id=self.machine_id, days=days, token=self.token
        )


@dataclass
class Token:
    token: str = random_token()
    api_client: APIClient = field(default_factory=APIClient)

    def add(self, dollars: int, currency: str) -> None:
        """Add to token"""
        self.api_client.token_add(token=self.token, dollars=dollars, currency=currency)

    def balance(self) -> int:
        """Returns the token's balance in cents."""
        return self.api_client.token_balance(token=self.token).cents

    def info(self) -> TokenInfo:
        """Returns information about a token."""
        return self.api_client.token_info(token=self.token)

    def invoices(self) -> List[Invoice]:
        """Returns invoices for adding balance to the token."""
        return self.api_client.token_invoices(token=self.token)

    def messages(self) -> List[api.TokenMessage]:
        """Returns support messages for/from the token."""
        return self.api_client.token_get_messages(token=self.token)

    def send_message(self, message: str) -> None:
        """Returns support messages for/from the token."""
        self.api_client.token_send_message(token=self.token, message=message)

    def servers(self, show_forgotten: bool = False) -> List[Server]:
        server_classes: List[Server] = []
        for server in self.api_client.servers_launched_from_token(self.token).servers:
            if not show_forgotten and server.forgotten_at is not None:
                continue
            server_classes.append(
                Server(
                    machine_id=server.machine_id,
                    api_client=self.api_client,
                    token=self.token,
                )
            )
        return server_classes

    def launch_server(
        self,
        ssh_key: str,
        flavor: str,
        days: int,
        operating_system: str,
        region: Union[str, None] = None,
        hostname: str = "",
        autorenew: bool = False,
        machine_id: str = random_machine_id(),
    ) -> Server:
        self.api_client.server_launch(
            machine_id=machine_id,
            days=days,
            token=self.token,
            region=region,
            flavor=flavor,
            operating_system=operating_system,
            ssh_key=ssh_key,
            hostname=hostname,
            autorenew=autorenew,
        )
        return Server(
            machine_id=machine_id, api_client=self.api_client, token=self.token
        )


@dataclass
class Client:
    client_token: str = ""
    """Token to manage/pay for servers with."""
    api_client: APIClient = field(default_factory=APIClient)
    """Your own API Client, perhaps if you want to connect through Tor."""

    def flavors(self) -> api.Flavors.Response:
        """Returns available flavors (server sizes)."""
        return self.api_client.flavors()

    def operating_systems(self) -> api.OperatingSystems.Response:
        """Returns available operating systems."""
        return self.api_client.operating_systems()

    def regions(self) -> api.Regions.Response:
        """Returns regions that servers can be launched in."""
        return self.api_client.regions()

    def server_quote(self, days: int, flavor: str) -> api.ServerQuote.Response:
        """Get a quote for how much a server will cost."""
        return self.api_client.server_quote(days=days, flavor=flavor)

    def changelog(self) -> str:
        """Read the API changeog."""
        return self.api_client.changelog()

    @property
    def token(self) -> Token:
        """Returns a Token object with the api_client and token specified."""
        return Token(token=self.client_token, api_client=self.api_client)
