import pytest
from dataclasses import dataclass
from enum import Enum
from pygindex.utils import PyGiJSONEncoder


def test_custom_json_encoder_enum():
    """Test enum values returned as strings"""
    class TestEnum(Enum):
        X = 1
    assert isinstance(PyGiJSONEncoder().default(TestEnum.X), str)


def test_custom_json_encoder_dataclass():
    """Test dataclasses returned as dictionaries"""
    @dataclass
    class TestDataclass:
        X: str = None
    data = TestDataclass(X="test")
    assert isinstance(PyGiJSONEncoder().default(data), dict)


def test_custom_json_encoder_other():
    """Test TypeError is raised for unhandled types"""
    with pytest.raises(TypeError):
        PyGiJSONEncoder().default(1)
