import pytest
from pygindex.models import IGAPIConfig


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


def test_prices_url():
    cfg = IGAPIConfig()
    assert cfg.prices_url.endswith("/prices")
