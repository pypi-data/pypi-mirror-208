"""SporeStack API request/response models"""


import sys
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .models import Flavor, Invoice, OperatingSystem, Payment, Region

if sys.version_info >= (3, 9):  # pragma: nocover
    from typing import Annotated
else:  # pragma: nocover
    from typing_extensions import Annotated


class TokenAdd:
    url = "/token/{token}/add"
    method = "POST"

    class Request(BaseModel):
        currency: str
        """BREAKING: This will change to models.Currency in version 11."""
        dollars: int
        affiliate_token: Union[str, None] = None

    class Response(BaseModel):
        token: Annotated[str, Field(deprecated=True)]
        payment: Annotated[Payment, Field(deprecated=True)]
        invoice: Invoice


class TokenBalance:
    url = "/token/{token}/balance"
    method = "GET"

    class Response(BaseModel):
        token: Annotated[str, Field(deprecated=True)]
        cents: int
        usd: str


class ServerQuote:
    url = "/server/quote"
    method = "GET"

    """Takes days and flavor as parameters."""

    class Response(BaseModel):
        cents: Annotated[
            int, Field(ge=1, title="Cents", description="(US) cents", example=1_000_00)
        ]
        usd: Annotated[
            str,
            Field(
                min_length=5,
                title="USD",
                description="USD in $1,000.00 format",
                example="$1,000.00",
            ),
        ]


class ServerLaunch:
    url = "/server/{machine_id}/launch"
    method = "POST"

    class Request(BaseModel):
        days: int
        flavor: str
        ssh_key: str
        operating_system: str
        region: Optional[str] = None
        """null is automatic, otherwise a string region slug."""
        token: str
        """Token to draw from when launching the server."""
        hostname: str = ""
        """Hostname to refer to your server by."""
        autorenew: bool = False
        """
        Automatically renew the server with the token used, keeping it at 1 week
        expiration.
        """


class ServerTopup:
    url = "/server/{machine_id}/topup"
    method = "POST"

    class Request(BaseModel):
        days: int
        token: Union[str, None] = None


class ServerDeletedBy(str, Enum):
    EXPIRATION = "expiration"
    """The server was deleted automatically for being expired."""
    MANUAL = "manual"
    """The server was deleted before its expiration via the API."""
    SPORESTACK = "sporestack"
    """The server was deleted by SporeStack, likely due to an AUP violation."""


class ServerInfo:
    url = "/server/{machine_id}/info"
    method = "GET"

    class Response(BaseModel):
        created_at: int
        expiration: int
        running: bool
        machine_id: str
        token: str
        ipv4: str
        ipv6: str
        region: str
        flavor: Flavor
        deleted: bool
        deleted_at: int
        deleted_by: Union[ServerDeletedBy, None]
        forgotten_at: Union[datetime, None]
        operating_system: str
        hostname: str
        autorenew: bool


class ServerStart:
    url = "/server/{machine_id}/start"
    method = "POST"


class ServerStop:
    url = "/server/{machine_id}/stop"
    method = "POST"


class ServerDelete:
    url = "/server/{machine_id}"
    method = "DELETE"


class ServerForget:
    url = "/server/{machine_id}/forget"
    method = "POST"


class ServerRebuild:
    url = "/server/{machine_id}/rebuild"
    method = "POST"


class ServerEnableAutorenew:
    url = "/server/{machine_id}/autorenew/enable"
    method = "POST"


class ServerDisableAutorenew:
    url = "/server/{machine_id}/autorenew/disable"
    method = "POST"


class ServersLaunchedFromToken:
    url = "/token/{token}/servers"
    method = "GET"

    class Response(BaseModel):
        servers: List[ServerInfo.Response]


class Flavors:
    url = "/flavors"
    method = "GET"

    class Response(BaseModel):
        flavors: Dict[str, Flavor]


class OperatingSystems:
    url = "/operatingsystems"
    method = "GET"

    class Response(BaseModel):
        operating_systems: Dict[str, OperatingSystem]


class Regions:
    url = "/regions"
    method = "GET"

    class Response(BaseModel):
        regions: Dict[str, Region]


class TokenMessageSender(str, Enum):
    USER = "User"
    SPORESTACK = "SporeStack"


class TokenMessage(BaseModel):
    message: str = Field(
        ...,
        title="Message",
        min_length=1,
        max_length=10_000,
    )
    sent_at: datetime = Field(
        ...,
        title="Sent At",
        description="When the message was sent.",
    )
    sender: TokenMessageSender = Field(
        ..., title="Sender", description="Who sent the message."
    )
