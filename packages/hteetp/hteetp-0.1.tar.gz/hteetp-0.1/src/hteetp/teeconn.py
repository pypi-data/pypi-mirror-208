from typing import Callable, TypeAlias

import socket
import io
import pathlib
from http.client import HTTPConnection, HTTPResponse

from .teereader import TeeReadingFile


FilepathFactory: TypeAlias = Callable[[str, str, str | int, str], pathlib.Path]


class TeeHTTPResponse(HTTPResponse):
    """
    A HTTPResponse which copies all the data read from the socket to a file.

    It still acts like a normal HTTPResponse in all other ways.
    """

    def __init__(self, file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fp = TeeReadingFile(src=self.fp, dst=file)


class TeeHTTPConnection(HTTPConnection):
    """
    A HTTPConnection which copies all the data read from the socket to files.

    The files are determined by a filepath_factory, which is a function which
    takes the method, host, port and url and returns a pathlib.Path.

    This class is not safe for concurrent use.
    """

    def __init__(self, filepath_factory: FilepathFactory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filepath_factory = filepath_factory

    def request(self, method: str, url: str, *args, **kwargs):
        path = self.filepath_factory(method, self.host, self.port, url)

        # The internal machinery of HTTPConnection ought to close this for us.
        self._file = open(path, "wb")

        # Closure to capture the file in the response_class function.
        def response_class(*args, **kwargs):
            return TeeHTTPResponse(self._file, *args, **kwargs)

        self.response_class = response_class

        return super().request(method, url, *args, **kwargs)


def static_filepath(path: pathlib.Path) -> FilepathFactory:
    """
    Demonstrates a filepath_factory which always returns the same file.
    """

    def factory(method: str, host: str, port: str | int, url: str) -> pathlib.Path:
        return path

    return factory


def relative_files(root: pathlib.Path) -> FilepathFactory:
    def factory(method: str, host: str, port: str | int, url: str) -> pathlib.Path:
        path = root / f"{method}/{host}:{port}/{url}"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    return factory


__all__ = ["TeeHTTPResponse", "TeeHTTPConnection", "static_filepath", "relative_files"]
