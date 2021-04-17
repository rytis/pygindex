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
    """Check if we have internal data structures set
    """
    assert isinstance(ig_client._auth, IGUserAuth)
    assert isinstance(ig_client._api, IGAPIConfig)


def test_request(monkeypatch):
    """Test if request abstraction helper returns correct data structures
    """

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
    """Test that we detect expired sessions
    """
    ig_client._session.expires = int(time.time()) - 1000
    assert ig_client._authentication_is_valid is False


def test_session_invalid_no_token(ig_client):
    """Test that we detect missing security token
    """
    session_data = IGSession(cst="abcdefg",
                             expires=int(time.time())+1000)
    ig_client._session = session_data
    assert ig_client._authentication_is_valid is False


def test_session_invalid_no_cst(ig_client):
    """Test that we detect missing CST
    """
    session_data = IGSession(security_token="abcdefg",
                             expires=int(time.time())+1000)
    ig_client._session = session_data
    assert ig_client._authentication_is_valid is False


def test_session_valid(ig_client):
    """Test we recognise valid session state
    """
    session_data = IGSession(cst="abcdefg",
                             security_token="abcdefg",
                             expires=int(time.time())+1000)
    ig_client._session = session_data
    assert ig_client._authentication_is_valid is True


def test_authentication(monkeypatch, ig_client):
    """Test we can retrieve authentication details
    """

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


def test_authenticated_request(mocker, ig_client):
    """Test we can perform authenticated request
    """
    mocker.patch.object(ig_client, "_request", return_value=None)
    res = ig_client._authenticated_request("https://example.com",
                                           "get",
                                           headers={},
                                           data={})
    ig_client._request.assert_called()


def test_get_session_details(mocker, ig_client):
    """Test getting session details from correct URL, and passing data back
    """
    mock_ret = IGResponse(data={"d_key": "d_val"}, headers={"h_key": "h_val"})
    mocker.patch.object(ig_client, "_authenticated_request", return_value=mock_ret)
    data = ig_client.get_session_details()
    ig_client._authenticated_request.assert_called_with(url=ig_client._api.session_url, method="get")
    assert data == {"d_key": "d_val"}


def test_get_accounts(mocker, ig_client):
    """Test getting account details from correct URL, and passing data back
    """
    mock_ret = IGResponse(data={"d_key": "d_val"}, headers={"h_key": "h_val"})
    mocker.patch.object(ig_client, "_authenticated_request", return_value=mock_ret)
    data = ig_client.get_accounts()
    ig_client._authenticated_request.assert_called_with(url=ig_client._api.accounts_url, method="get")
    assert data == {"d_key": "d_val"}


def test_get_positions(mocker, ig_client):
    """Test getting positions from correct URL, and passing data back
    """
    mock_ret = IGResponse(data={"d_key": "d_val"}, headers={"h_key": "h_val"})
    mocker.patch.object(ig_client, "_authenticated_request", return_value=mock_ret)
    data = ig_client.get_positions()
    ig_client._authenticated_request.assert_called_with(url=ig_client._api.positions_url, method="get")
    assert data == {"d_key": "d_val"}


def test_search_markets(mocker, ig_client):
    """Test searching markets from correct URL, and passing data back
    """
    mock_ret = IGResponse(data={"d_key": "d_val"}, headers={"h_key": "h_val"})
    mocker.patch.object(ig_client, "_authenticated_request", return_value=mock_ret)
    data = ig_client.search_markets("test")
    ig_client._authenticated_request.assert_called_with(url=ig_client._api.markets_url,
                                                        method="get",
                                                        data={"searchTerm": "test"})
    assert data == {"d_key": "d_val"}
