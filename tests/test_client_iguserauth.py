
import random
import string
import pytest
from pygindex.models import IGUserAuth


def random_str(length=10):
    return "".join(random.choice(string.ascii_letters) for i in range(length))


TEST_INIT_DATA = {"api_key": random_str(),
                  "username": random_str(),
                  "password": random_str()}


@pytest.fixture(scope="module")
def ig_user_auth():
    auth = IGUserAuth(**TEST_INIT_DATA)
    return auth


def test_auth_logon_details(ig_user_auth):
    assert ig_user_auth.username == TEST_INIT_DATA["username"]
    assert ig_user_auth.password == TEST_INIT_DATA["password"]
    assert ig_user_auth.api_key == TEST_INIT_DATA["api_key"]


def test_auth_req_headers(ig_user_auth):
    assert "X-IG-API-KEY" in ig_user_auth.auth_req_headers
    assert "Content-Type" in ig_user_auth.auth_req_headers
    assert ig_user_auth.auth_req_headers["X-IG-API-KEY"] == ig_user_auth.api_key
    assert ig_user_auth.auth_req_headers["Content-Type"] == "application/json"


def test_auth_req_data(ig_user_auth):
    assert "identifier" in ig_user_auth.auth_req_data
    assert "password" in ig_user_auth.auth_req_data
    assert "encryptedPassword" in ig_user_auth.auth_req_data
    assert ig_user_auth.auth_req_data["identifier"] == \
           TEST_INIT_DATA["username"]
    assert ig_user_auth.auth_req_data["password"] == TEST_INIT_DATA["password"]
    assert ig_user_auth.auth_req_data["encryptedPassword"] is None
