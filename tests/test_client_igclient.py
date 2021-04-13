import time
import pytest
import requests
from pygindex.client import IGClient, IGAPIConfig, IGUserAuth, \
    IGResponse, IGSession


@pytest.fixture(scope="module")
def ig_client():
    client = IGClient(IGUserAuth("api_key", "username", "password"),
                      IGAPIConfig("demo"))
    return client


def test_client(ig_client):
    assert isinstance(ig_client._auth, IGUserAuth)
    assert isinstance(ig_client._api, IGAPIConfig)


def test_request(monkeypatch):

    class MockResp:
        def __init__(self):
            self.status_code = 200
            self.url = "http://example.com"
            self.headers = {"h_key": "h_value"}

        def json(self):
            return {"d_key": "d_value"}

    def req_get(*args, **kwargs):
        return MockResp()

    monkeypatch.setattr(requests, "get", req_get)

    res = IGClient._request("https://example.com",
                            "get",
                            {"d_key": "d_val"},
                            {"h_key": "h_val"})

    assert isinstance(res, IGResponse)
    assert res.data == {"d_key": "d_value"}
    assert res.headers == {"h_key": "h_value"}


def test_session_invalid_timed_out(ig_client):
    ig_client._session.expires = int(time.time()) - 1000
    assert ig_client._authentication_is_valid is False


def test_session_invalid_no_token(ig_client):
    session_data = IGSession(cst="abcdefg",
                             expires=int(time.time())+1000)
    ig_client._session = session_data
    assert ig_client._authentication_is_valid is False


def test_session_invalid_no_cst(ig_client):
    session_data = IGSession(security_token="abcdefg",
                             expires=int(time.time())+1000)
    ig_client._session = session_data
    assert ig_client._authentication_is_valid is False


def test_session_valid(ig_client):
    session_data = IGSession(cst="abcdefg",
                             security_token="abcdefg",
                             expires=int(time.time())+1000)
    ig_client._session = session_data
    assert ig_client._authentication_is_valid is True


def test_authentication(monkeypatch, ig_client):

    class MockResp:
        def __init__(self):
            self.status_code = 200
            self.url = "http://example.com"
            self.headers = {"Access-Control-Max-Age": "3600",
                            "CST": "abcdefg",
                            "X-SECURITY-TOKEN": "gfedcba"}

        def json(self):
            return {"d_key": "d_value"}

    def req_post(*args, **kwargs):
        return MockResp()

    monkeypatch.setattr(requests, "post", req_post)

    ig_client._authenticate()

    assert ig_client._session.cst == "abcdefg"