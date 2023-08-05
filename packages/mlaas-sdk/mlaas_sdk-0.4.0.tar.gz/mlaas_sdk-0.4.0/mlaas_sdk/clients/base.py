from ..utils import parse_base_url


class BaseClient(object):
    def __init__(self, endpoint: str, secure: bool = False):
        self.base = parse_base_url(endpoint, secure)

    def build_url(self, *paths: str) -> str:
        return "/".join([self.base.lstrip("/")] + [p.strip("/") for p in paths])
