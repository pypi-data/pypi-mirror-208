from urllib.parse import urlparse, urlunparse


def parse_base_url(url, secure=False):
    parsed_url = urlparse(url)
    scheme = "https" if secure else "http"
    netloc = parsed_url.netloc.rstrip("/")
    if not parsed_url.scheme:
        netloc = scheme + "://" + netloc
    return urlunparse((scheme, netloc, "", "", "", ""))
