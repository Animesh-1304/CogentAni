from auth import hash_password, verify_password


def test_hash_password():
    password = "TestPassword123!"

    password_hash = hash_password(password)

    assert password_hash != password
    assert password_hash.startswith("$argon2")


def test_verify_password():
    password = "TestPassword123!"

    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True


def test_verify_wrong_password():
    password = "TestPassword123!"

    password_hash = hash_password(password)

    assert verify_password("WrongPassword123!", password_hash) is False