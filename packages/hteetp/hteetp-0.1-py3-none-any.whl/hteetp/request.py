from typing import Optional
import pathlib

from .teeconn import TeeHTTPConnection, TeeHTTPResponse, static_filepath


def http_request(
    filepath: pathlib.Path, method: str, host: str, path: str, port: Optional[str | int] = None, *args, **kwargs
) -> TeeHTTPResponse:
    """
    Makes a HTTP request to the given host and path, and saves the response to the given filename,
    but also returns the HTTP response object.

    If port is not given, it will be inferred from the scheme.

    args and kwargs are passed to the http.client.HTTPConnection constructor.
    """
    conn = TeeHTTPConnection(static_filepath(filepath), host, port, *args, **kwargs)
    conn.request(method, path)
    return conn.getresponse()


__all__ = ["http_request"]
