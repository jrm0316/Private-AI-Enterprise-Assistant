from fastapi import APIRouter, Depends, Request
from auth.auth_bearer import JWTBearer, get_current_user

import os
import json

router = APIRouter()

HISTORY_DIR = "history"

os.makedirs(HISTORY_DIR, exist_ok=True)

# =========================
# GET HISTORY
# =========================
@router.get(
    "/history",
    dependencies=[Depends(JWTBearer())]
)
def get_history(request: Request):

    user_id = get_current_user(request)

    history_path = os.path.join(
        HISTORY_DIR,
        f"{user_id}.json"
    )

    if not os.path.exists(history_path):
        return {
            "success": True,
            "data": []
        }

    with open(history_path, "r", encoding="utf-8") as f:
        messages = json.load(f)

    return {
        "success": True,
        "data": messages
    }

# =========================
# CLEAR HISTORY
# =========================
@router.delete(
    "/clear-history",
    dependencies=[Depends(JWTBearer())]
)
def clear_history(request: Request):

    user_id = get_current_user(request)

    history_path = os.path.join(
        HISTORY_DIR,
        f"{user_id}.json"
    )

    if os.path.exists(history_path):
        os.remove(history_path)

    return {
        "success": True,
        "message": "Histórico apagado"
    }

# =========================
# SAVE MESSAGE
# =========================

def save_message(user_id, role, content):

    history_path = os.path.join(
        HISTORY_DIR,
        f"{user_id}.json"
    )

    messages = []

    # =========================
    # LOAD EXISTING
    # =========================

    if os.path.exists(history_path):

        with open(history_path, "r", encoding="utf-8") as f:
            messages = json.load(f)

    # =========================
    # APPEND
    # =========================

    messages.append({
        "role": role,
        "content": content
    })

    # =========================
    # SAVE
    # =========================

    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(
            messages,
            f,
            ensure_ascii=False,
            indent=2
        )