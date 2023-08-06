from hteetp import http_request, http_response_from_file

def test_http_request_GET(tmp_path):
    file = tmp_path / "test.http"
    resp = http_request(file, 'GET', 'www.google.com', "/")
    data = resp.read()
    assert data

    have = http_response_from_file(file)
    assert have.read() == data
    assert have.headers.items() == resp.headers.items()

