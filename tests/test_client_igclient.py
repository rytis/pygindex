import requests
from pygindex.client import IGClient, IGAPIConfig, IGUserAuth, IGResponse


def test_client():
    client = IGClient(IGUserAuth("api_key", "user_name", "password"),
                      IGAPIConfig("demo"))
    assert isinstance(client._auth, IGUserAuth)
    assert isinstance(client._api, IGAPIConfig)


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

