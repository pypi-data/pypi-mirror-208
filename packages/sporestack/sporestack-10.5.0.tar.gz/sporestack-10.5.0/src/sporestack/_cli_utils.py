def cents_to_usd(cents: int) -> str:
    """cents_to_usd: Convert cents to USD string."""
    return f"${cents * 0.01:,.2f}"


def mb_string(megabytes: int) -> str:
    """Returns a formatted string for megabytes."""
    if megabytes < 1024:
        return f"{megabytes} MiB"

    return f"{megabytes // 1024} GiB"


def gb_string(gigabytes: int) -> str:
    """Returns a formatted string for gigabytes."""
    if gigabytes < 1000:
        return f"{gigabytes} GiB"

    return f"{gigabytes / 1000} TiB"


def tb_string(terabytes: float) -> str:
    """Returns a formatted string for terabytes."""
    return f"{terabytes} TiB"
