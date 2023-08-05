import secrets
from base64 import b16encode
from struct import pack
from zlib import adler32


def checksum(to_hash: str) -> str:
    """
    Base 16 string of half the adler32 checksum
    """
    adler32_hash = adler32(bytes(to_hash, "utf-8"))
    return b16encode(pack("I", adler32_hash)).decode("utf-8").lower()[-4:]


def random_machine_id() -> str:
    """
    Machine IDs have a 32 character format with a checksum.
    """
    to_hash = f"ss_m_{secrets.token_hex(11)}"
    return f"{to_hash}_{checksum(to_hash)}"


def random_token() -> str:
    """
    Tokens have a 32 character format with a checksum.
    """
    to_hash = f"ss_t_{secrets.token_hex(11)}"
    return f"{to_hash}_{checksum(to_hash)}"
