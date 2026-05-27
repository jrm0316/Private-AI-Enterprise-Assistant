from fastapi import APIRouter, Request, Depends
import os
import json

from auth.auth_bearer import (
    JWTBearer,
    get_current_user
)

router = APIRouter()

CHAT_HISTORY_DIR = "chat_history"

# =========================
# CLEAR HISTORY
# =========================
@router.delete(
    "/clear-history",
    dependencies=[Depends(JWTBearer())]
)
def clear_history(request: Request):

    user_id = get_current_user(request)

    user_file = os.path.join(
        CHAT_HISTORY_DIR,
        f"{user_id}.json"
    )

    # APAGA HISTÓRICO
    if os.path.exists(user_file):

        with open(user_file, "w", encoding="utf-8") as f:
            json.dump([], f)

    return {
        "success": True,
        "message": "Histórico apagado"
    }