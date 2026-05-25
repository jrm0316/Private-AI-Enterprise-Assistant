from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import compare_with_job

router = APIRouter()

class CompareRequest(BaseModel):
    resume: str
    job: str

@router.post("/compare")
def compare(req: CompareRequest):

    try:
        result = compare_with_job(req.resume, req.job)

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