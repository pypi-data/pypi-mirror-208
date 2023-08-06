import pytest

from eossr.api.zenodo import http_status


def test_ZenodoHTTPStatus():

    # good status, no error raised
    status = http_status.ZenodoHTTPStatus(200)
    assert status.code == 200
    assert status.name == 'OK'
    assert status.is_error() is False
    status.raise_error()  # does nothing

    # bad status, must raise an HTTPStatusError
    pytest.raises(
        http_status.HTTPStatusError,
        http_status.ZenodoHTTPStatus,
        400,
    )

    # wrong status code, must raise a ValueError
    pytest.raises(
        ValueError,
        http_status.ZenodoHTTPStatus,
        324324,
    )
