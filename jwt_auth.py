import os

from datetime import datetime, timedelta, timezone

from jose import jwt
from dotenv import load_dotenv


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

if __name__ == "__main__":
    token = create_access_token({
        "sub": "1"
    })

    print(token)