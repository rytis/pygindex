import pytest
from pygindex.client import IGAPIConfig


def test_valid_env_var(monkeypatch):
    monkeypatch.setenv("IG_PLATFORM", "demo")
    cfg = IGAPIConfig()
    assert cfg.base_url == "https://demo-api.ig.com/gateway/deal"


def test_invalid_env_var(monkeypatch):
    monkeypatch.setenv("IG_PLATFORM", "does_not_exist")
    with pytest.raises(ValueError):
        cfg = IGAPIConfig()


def test_session_url():
    cfg = IGAPIConfig()
    assert cfg.session_url.endswith("/session")


def test_accounts_url():
    cfg = IGAPIConfig()
    assert cfg.accounts_url.endswith("/accounts")


def test_positions_url():
    cfg = IGAPIConfig()
    assert cfg.positions_url.endswith("/positions")


def test_markets_url():
    cfg = IGAPIConfig()
    assert cfg.markets_url.endswith("/markets")
