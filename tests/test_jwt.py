from jwt_auth import create_access_token, verify_access_token


def test_create_access_token():
    token = create_access_token(
        data={"sub": "1"}
    )

    assert token is not None
    assert isinstance(token, str)


def test_verify_access_token():
    token = create_access_token(
        data={"sub": "1"}
    )

    payload = verify_access_token(token)

    assert payload is not None
    assert payload["sub"] == "1"


def test_verify_invalid_token():
    payload = verify_access_token("invalid-token")

    assert payload is None