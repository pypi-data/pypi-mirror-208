from unittest.mock import patch, Mock
import pytest
from ucampurestorage.lib.tokencreater import TokenCreater as token


@pytest.fixture
def tokenlib() -> token:
    return token()


@pytest.mark.parametrize(
    "date, expected",
    [
        ("17-May-20 00:00:00", "17-May-20 00:00:00"),
        ("17-May-22 00:00:00", "17-May-22 00:00:00"),
    ],
)
def test_token_token_create_datetime(tokenlib, date, expected) -> None:
    token_date = tokenlib.token_create_datetime(token_cdatetime=date)
    assert token_date == expected


@pytest.mark.parametrize(
    "date, expected",
    [
        ("17-May-20 00:00:00", "17-May-20 00:00:00"),
        ("17-May-22 00:00:00", "17-May-22 00:00:00"),
    ],
)
def test_token_token_current_token_modify(tokenlib, date, expected) -> None:
    token_date = tokenlib.current_token_modify(new_token=date)
    assert token_date == expected


def test_token_token_generation(tokenlib) -> None:
    with patch(
        "ucampurestorage.lib.tokencreater.TokenCreater._get_private_key"
    ) as pvt_key:
        pvt_key.return_value = "xadas1231"
        with patch(
            "ucampurestorage.lib.tokencreater.TokenCreater._generate_id_token"
        ) as token:
            token.return_value = "yuytuy11"
            with patch(
                "ucampurestorage.lib.tokencreater.TokenCreater._get_access_token"
            ) as acc_token:
                acc_token.return_value = "xaw.g123"
                token_gen = tokenlib.token_generation(
                    "1231", "9999", "user", "./tmp.txt", "apiuser", "puresg.com"
                )
                assert token_gen == "xaw.g123"


def test_token__get_access_token(tokenlib) -> None:
    with patch("requests.post") as response:
        response.return_value.close = Mock()
        response.return_value.json.return_value = {
            "access_token": "eyJ5lb1VHR.eyJhdWRlYjIxIn0.qk1QuJ5g",
            "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "token_type": "Bearer",
            "expires_in": 86399,
        }
        return_val = tokenlib._get_access_token("1231", "pure.com")
        assert return_val == "eyJ5lb1VHR.eyJhdWRlYjIxIn0.qk1QuJ5g"
