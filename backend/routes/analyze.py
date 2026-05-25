from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import analyze_resume

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str

@router.post("/analyze")
def analyze(req: AnalyzeRequest):

    try:
        result = analyze_resume(req.text)

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