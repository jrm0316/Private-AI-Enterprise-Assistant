from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import compare_documents

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str

@router.post("/analyze")
def analyze(req: AnalyzeRequest):

    try:
        response = compare_documents(req.text)

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