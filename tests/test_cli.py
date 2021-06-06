import pytest
from datetime import datetime, timedelta
from dateutil import tz
from pygindex.cli import app, InstrumentCommand


def test_api():
    with pytest.raises(SystemExit) as exc:
        app()
    assert exc.type == SystemExit
    assert exc.value.code == 2


def test_date_parsing_datetime():
    """Test parsing date time strings"""
    assert InstrumentCommand._parse_date("2021/1/20") == datetime(2021, 1, 20, tzinfo=tz.tzutc())
    assert InstrumentCommand._parse_date("2021/1/20 10:20") == datetime(2021, 1, 20, 10, 20, tzinfo=tz.tzutc())


def test_date_parsing_relative():
    """Test parsing relative 'human language' date time strings"""
    real_2d_ago = datetime.now(tz=tz.tzlocal()) - timedelta(days=2)
    test_2d_ago = InstrumentCommand._parse_date("2 days ago")
    time_delta = test_2d_ago - real_2d_ago
    assert time_delta.seconds < 2  # we should have relatively close times


def test_date_parsing_now():
    """Test we respond to 'now' keyword"""
