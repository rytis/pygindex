from pygindex.client import IGClient, IGAPIConfig, IGUserAuth


def test_client():
    client = IGClient(IGUserAuth("api_key", "user_name", "password"),
                      IGAPIConfig("demo"))
    assert isinstance(client._auth, IGUserAuth)
    assert isinstance(client._api, IGAPIConfig)
