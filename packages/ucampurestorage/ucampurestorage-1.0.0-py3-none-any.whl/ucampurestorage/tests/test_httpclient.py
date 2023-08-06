import pytest
from ucampurestorage.lib.httpclient import HttpClient as clientHttp


@pytest.fixture
def httpconnect() -> clientHttp:
    return clientHttp("purestorage.com", 443, "user", "password", "121xx1231", True)


def test_http_check_url(httpconnect) -> None:
    assert httpconnect.base_url == "https://purestorage.com:443/api/2.17/"


def test_http_check_token(httpconnect) -> None:
    assert httpconnect.header["Authorization"] == "Bearer 121xx1231"


@pytest.mark.parametrize("base", ["/", "/volumes/", "/v/t1"])
def test_http_format_url(httpconnect, base) -> None:
    URI = "https://purestorage.com:443/api/2.17"
    url = httpconnect._format_url(base)
    assert url == f"{URI}{base}"
