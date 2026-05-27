from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import compare_documents

router = APIRouter()

class MatchRequest(BaseModel):
    resume: str
    job: str

@router.post("/match")
def match(data: MatchRequest):

    result = compare_documents(
        data.resume,
        data.job
    )

    return result