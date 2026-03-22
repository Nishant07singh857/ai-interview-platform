# app/api/v1/endpoints/gemini.py
"""
Gemini AI endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from app.core.deps import get_current_user
from app.models.user import User
from app.services.gemini_service import gemini_service

router = APIRouter()

@router.get("/test")
async def test_gemini(current_user: User = Depends(get_current_user)):
    """Test Gemini integration"""
    try:
        questions = await gemini_service.generate_questions_for_topic(
            subject="Machine Learning",
            topic="Linear Regression",
            count=2
        )
        return {
            "success": True,
            "message": f"Generated {len(questions)} questions",
            "questions": questions
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/generate")
async def generate_questions(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Generate questions for a topic"""
    topic = request.get("topic")
    count = request.get("count", 5)
    subject = request.get("subject", "Machine Learning")
    
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    
    questions = await gemini_service.generate_questions_for_topic(
        subject=subject,
        topic=topic,
        count=count
    )
    
    return {
        "success": True,
        "questions": questions
    }