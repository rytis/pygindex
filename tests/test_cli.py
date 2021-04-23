import pytest
from pygindex.cli import app


def test_api():
    with pytest.raises(SystemExit) as exc:
        app()
    assert exc.type == SystemExit
    assert exc.value.code == 2
