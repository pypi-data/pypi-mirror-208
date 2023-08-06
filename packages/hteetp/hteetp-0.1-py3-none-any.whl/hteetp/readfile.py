import pathlib
from http.client import HTTPResponse


class _MockSocket:
    """
    Utility to make it so sock.makefile returns a file object.
    """

    def __init__(self, filepath: pathlib.Path):
        self.filepath = filepath

    def makefile(self, *args, **kwargs):
        return open(self.filepath, *args, **kwargs)


def http_response_from_file(filepath: pathlib.Path) -> HTTPResponse:
    """
    Read an HTTPResponse from a file.

    :param filepath: The path to the file to read.
    :return: The HTTPResponse object. The headers have been read, but the body has not.
    """
    sock = _MockSocket(filepath)
    response = HTTPResponse(sock)
    response.begin()
    return response


__all__ = [
    'http_response_from_file',
]
