from requests import Response, HTTPError


class CliException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def raise_for_status(r: Response, msg: str):
    try:
        r.raise_for_status()
    except HTTPError as e:
        raise CliException(msg) from e
