import pytest
from datetime import datetime
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


def test_date_parsing_now():
    """Test we respond to 'now' keyword"""
