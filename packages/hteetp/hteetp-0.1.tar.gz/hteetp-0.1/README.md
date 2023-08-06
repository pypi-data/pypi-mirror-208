# hteetp

[![PyPI - Version](https://img.shields.io/pypi/v/hteetp.svg)](https://pypi.org/project/hteetp)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hteetp.svg)](https://pypi.org/project/hteetp)

`hteetp` is a Python package for copying HTTP responses to disk. It
provides wrappers around the standard library's `http.client`
infrastructure.

This is useful when making something that should capture traffic,
either for later analysis or for a cache.

It's like `tee` but for HTTP requests.

## Installation

```console
pip install hteetp
```

## Usage

The simplest usage is `hteetp.http_request`:

```python
from hteetp import http_request


def request_and_record():
	response = http_request("./snapshot.http", "GET", "github.com", "/spenczar/hteetp")
	# Now the file ./snapshot.http exists - but it will only have headers and the 
	# 'HTTP/1.1' preamble
	
	response_data = response.read()
	# Now the file will be populated with the contents of response_data
	
	assert len(response.headers) > 0
	assert len(response_data) != 0
```


### Long-lived connections

Alternatively, `hteetp.TeeHTTPConnection` is a replacement for
`http.client.HTTPConnection`. You provide it with a function for
generating filepaths given HTTP request parameters, and it manages the
`tee`ing for you. This gives you a long-lived connection if you're
hitting the same host many times.

```python
from hteetp import TeeHTTPConnection, relative_files


def request_and_record():
	conn = TeeHTTPConnection(relative_files("./snapshots") "github.com")
	for path in ["/spenczar/hteetp", "/python/cpython", "/psf/requests"]:
		resp = conn.request("GET", path)
		resp_data = resp.read()
		# handle each response
	# The following files will have been written:
	# ./snapshots/GET/github.com:443/spenczar/hteetp
	# ./snapshots/GET/github.com:443/python/cpython	
	# ./snapshots/GET/github.com:443/psf/requests	

```


### Reading HTTP from files on disk

`hteetp.http_response_from_file` is a little utility for loading a
`http.client.HTTPResponse` from a file on disk:

```python
from hteetp import http_response_from_file

resp = http_response_from_file("./snapshots/GET/github.com:443/spenczar/hteetp")
print(resp.headers)
resp_body = resp.read()
print(resp_body)
```
