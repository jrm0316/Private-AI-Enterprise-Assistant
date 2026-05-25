from jose import jwt
from jose.exceptions import JWTError

from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

print("AUTH_HANDLER SECRET:", SECRET_KEY)

# =====================================================
# CONFIG JWT
# =====================================================

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

# =====================================================
# CRIAR TOKEN
# =====================================================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# =====================================================
# VALIDAR TOKEN
# =====================================================

def verify_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        return None