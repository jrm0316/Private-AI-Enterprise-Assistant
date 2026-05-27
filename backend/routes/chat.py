from fastapi import APIRouter, Depends
from pydantic import BaseModel

from services.ai_service import compare_documents
from services.ai_service import load_chat_history
from fastapi import Request

from auth.auth_bearer import (
    JWTBearer,
    get_current_user
)

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    selected_document: str | None = None

@router.post("/chat", dependencies=[Depends(JWTBearer())])
def chat(
    request: Request,
    req: ChatRequest
):

    user_id = get_current_user(request)

    try:

        # =========================
        # LOAD HISTORY
        # =========================

        history = load_chat_history(user_id)

        # =========================
        # AI RESPONSE
        # =========================

        result = compare_documents(
            user_id,
            req.question,
            history,
            req.selected_document
        )

        return {
            "success": True,
            "data": result,
            "error": None
        }

    except Exception as e:

        return {
            "success": False,
            "data": None,
            "error": str(e)
        }

@router.get(
    "/history",
    dependencies=[Depends(JWTBearer())]
)
def get_history(request: Request):

    user_id = get_current_user(request)

    history = load_chat_history(user_id)

    return {
        "success": True,
        "data": history
    }