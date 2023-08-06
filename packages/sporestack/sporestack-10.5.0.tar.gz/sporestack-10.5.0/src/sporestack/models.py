"""SporeStack API supplemental models"""

import sys
from enum import Enum
from typing import Optional, Union

if sys.version_info >= (3, 9):  # pragma: nocover
    from typing import Annotated
else:  # pragma: nocover
    from typing_extensions import Annotated

from pydantic import BaseModel, Field


class Currency(str, Enum):
    xmr = "xmr"
    """Monero"""
    btc = "btc"
    """Bitcoin"""
    bch = "bch"
    """Bitcoin Cash"""


class Payment(BaseModel):
    """This is deprecated in favor of Invoice."""

    txid: Optional[str]
    uri: Optional[str]
    usd: str
    paid: bool


class Flavor(BaseModel):
    # Unique string to identify the flavor that's sort of human readable.
    slug: str
    # Number of vCPU cores the server is given.
    cores: int
    # Memory in Megabytes
    memory: int
    # Disk in Gigabytes
    disk: int
    # USD cents per day
    price: int
    # IPv4 connectivity: "/32"
    ipv4: str
    # IPv6 connectivity: "/128"
    ipv6: str
    """Gigabytes of bandwidth per day."""
    bandwidth_per_month: float
    """Gigabytes of bandwidth per month."""


class OperatingSystem(BaseModel):
    slug: str
    """Unique string to identify the operating system."""
    minimum_disk: int
    """Minimum disk storage required in GiB"""
    provider_slug: str
    """Unique string to identify the operating system."""


class TokenInfo(BaseModel):
    balance_cents: int
    balance_usd: str
    burn_rate: int
    """Deprecated."""
    burn_rate_cents: int
    burn_rate_usd: str
    days_remaining: int
    servers: int


class Region(BaseModel):
    # Unique string to identify the region that's sort of human readable.
    slug: str
    # Actually human readable string describing the region.
    name: str


class Invoice(BaseModel):
    id: int
    payment_uri: Annotated[
        str, Field(description="Cryptocurrency URI for the payment.")
    ]
    cryptocurrency: Annotated[
        Currency,
        Field(description="Cryptocurrency that will be used to pay this invoice."),
    ]
    amount: Annotated[
        int,
        Field(
            description="Amount of cents to add to the token if this invoice is paid."
        ),
    ]
    fiat_per_coin: Annotated[
        str,
        Field(
            description="Stringified float of the price when this was made.",
            example="100.00",
        ),
    ]
    created: Annotated[
        int, Field(description="Timestamp of when this invoice was created.")
    ]
    expires: Annotated[
        int, Field(description="Timestamp of when this invoice will expire.")
    ]
    paid: Annotated[
        int, Field(description="Timestamp of when this invoice was paid. 0 if unpaid.")
    ]
    txid: Annotated[
        Union[str, None],
        Field(
            description="TXID of the transaction for this payment, if it was paid.",
            min_length=64,
            max_length=64,
            regex="^[a-f0-9]+$",
        ),
    ]
    expired: Annotated[
        bool,
        Field(
            description=(
                "Whether or not the invoice has expired (only applicable if "
                "unpaid, or payment not yet confirmed."
            ),
        ),
    ]
