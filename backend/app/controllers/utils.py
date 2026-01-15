from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.analysis_service import generate_job_description
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class GenerateJDRequest(BaseModel):
    job_role: str
    language: str = "en"  # Default to English

@router.post("/generate-jd")
async def generate_jd_endpoint(request: GenerateJDRequest):
    if not request.job_role:
        raise HTTPException(status_code=400, detail="Job role is required")
    
    try:
        jd = await generate_job_description(request.job_role, request.language)
        return {"job_description": jd}
    except Exception as e:
        logger.exception(f"Failed to generate JD: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate job description")

