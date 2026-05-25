from fastapi import APIRouter, HTTPException

from auth.users_db import (
    get_user,
    verify_password
)

from auth.auth_handler import create_access_token

router = APIRouter()


# =====================================================
# LOGIN
# =====================================================

@router.post("/login")
async def login(data: dict):

    email = data.get("email")
    password = data.get("password")

    user = get_user(email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado"
        )

    if not verify_password(
        password,
        user["hashed_password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Senha incorreta"
        )

    token = create_access_token(
        {
            "sub": user["email"]
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }