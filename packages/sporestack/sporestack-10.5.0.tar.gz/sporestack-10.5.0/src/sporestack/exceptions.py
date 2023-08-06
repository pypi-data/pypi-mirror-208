class SporeStackError(Exception):
    pass


class SporeStackUserError(SporeStackError):
    """HTTP 4XX"""

    pass


class SporeStackTooManyRequestsError(SporeStackError):
    """HTTP 429, retry again later"""

    pass


class SporeStackServerError(SporeStackError):
    """HTTP 5XX"""

    pass
