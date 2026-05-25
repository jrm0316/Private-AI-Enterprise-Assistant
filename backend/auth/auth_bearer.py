from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from jose import jwt, JWTError

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"

print("AUTH_BEARER SECRET:", SECRET_KEY)


class JWTBearer(HTTPBearer):

    async def __call__(self, request: Request):

        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if credentials:

            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=403,
                    detail="Token inválido"
                )

            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403,
                    detail="Token expirado ou inválido"
                )

            return credentials.credentials

        raise HTTPException(
            status_code=403,
            detail="Código inválido"
        )

    def verify_jwt(self, jwtoken: str) -> bool:

        try:

            payload = jwt.decode(
                jwtoken,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            print("TOKEN OK:", payload)

            return True

        except JWTError as e:
            print("VERIFY JWT ERROR:", e)
            return False


def get_current_user(request: Request):

    try:

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(
                status_code=401,
                detail="Token não enviado"
            )

        token = auth_header.replace("Bearer ", "")

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload.get("sub")

    except JWTError as e:

        print("JWT ERROR:", e)

        raise HTTPException(
            status_code=401,
            detail="Token expirado ou inválido"
        )