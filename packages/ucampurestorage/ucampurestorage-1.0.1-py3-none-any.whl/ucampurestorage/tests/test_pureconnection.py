from unittest.mock import patch, Mock
import pytest
from ucampurestorage.lib.httpclient import HttpClient
from ucampurestorage.lib.pureconnect import PureAdvanceConnection as pure
from ucampurestorage.lib.pureconnect import totalbytes, converttobytes
import logging

logger = logging.getLogger("PURE_LOGS")


@pytest.fixture
def init_pure() -> pure:
    return pure("pure.com", 443, "user", "password", "aweaw.1231.asdga", True)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("100k", 102400),
        ("100m", 104857600),
        ("100g", 107374182400),
        ("100t", 109951162777600),
        ("100p", 112589990684262400),
    ],
)
def test_pureconnect_totalbytes(input, expected) -> None:
    bsize = totalbytes(input)
    assert bsize == expected


@pytest.mark.parametrize(
    "input, unit,expected",
    [
        ("100", "k", 102400),
        ("100", "m", 104857600),
        ("100", "g", 107374182400),
        ("100", "t", 109951162777600),
        ("100", "p", 112589990684262400),
    ],
)
def test_pureconnect_converttobytes(input, expected, unit) -> None:
    bsize = converttobytes(input, unit)
    assert bsize == expected


@pytest.mark.parametrize("input, expected", [(200, True), (400, False), (302, False)])
def test_pureconnect__check_result(init_pure, input, expected) -> None:
    input_data = Mock()
    input_data.status_code = input
    code = init_pure._check_result(input_data)
    assert code == expected


def test_pureconnect_get_json_exception(caplog, init_pure) -> None:
    init_pure._get_json("123")
    assert "ERROR: invalid json" in caplog.text


def test_pureconnect_get_json(caplog, init_pure) -> None:
    blog = Mock()
    blog.json = 1231
    blog.json = Mock()
    init_pure._get_json(blog)
    assert "ERROR: invalid json" not in caplog.text


@pytest.mark.parametrize(
    "fetched",
    [
        {
            "continuation_token": None,
            "items": [
                {
                    "type": "array_controller",
                    "model": "FA-C60R3",
                    "status": "ready",
                    "mode": "secondary",
                    "version": "6.3.10",
                    "name": "CT0",
                },
                {
                    "type": "array_controller",
                    "model": "FA-C60R3",
                    "status": "ready",
                    "mode": "primary",
                    "version": "6.3.10",
                    "name": "CT1",
                },
            ],
            "more_items_remaining": False,
            "total_item_count": None,
        }
    ],
)
def test_pureconnect_get_controllers(init_pure, fetched) -> None:
    with patch.object(HttpClient, "get") as fetch:
        fetch.return_value.json.return_value = fetched
        fetch.return_value.status_code = 200
        return_val = init_pure.get_controllers()
        assert return_val is True
        assert init_pure.controllers == {
            "CT0": {
                "status": "ready",
                "model": "FA-C60R3",
                "mode": "secondary",
                "version": "6.3.10",
            },
            "CT1": {
                "status": "ready",
                "model": "FA-C60R3",
                "mode": "primary",
                "version": "6.3.10",
            },
        }
