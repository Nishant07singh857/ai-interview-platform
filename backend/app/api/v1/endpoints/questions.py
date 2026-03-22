"""
Questions Endpoints - Complete question management API
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from app.core.database import firebase_client
from app.core.deps import get_current_user, get_current_admin_user, get_current_pro_user
from app.models.user import User
from app.models.question import Question, DifficultyLevel, SubjectArea, QuestionType
from app.schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    QuestionDetailResponse, QuestionWithAnswerResponse,
    QuestionSearch, QuestionAttemptCreate, QuestionAttemptResponse,
    TopicResponse, QuestionSetResponse, QuestionSetDetailResponse
)
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])
logger = logging.getLogger(__name__)
question_service = QuestionService()

# Public endpoints (authenticated users)
@router.get("/", response_model=List[QuestionResponse])
async def get_questions(
    subject: Optional[SubjectArea] = None,
    topic: Optional[str] = None,
    difficulty: Optional[DifficultyLevel] = None,
    type: Optional[QuestionType] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """Get questions with filters"""
    try:
        questions = await question_service.get_questions(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            type=type,
            limit=limit,
            offset=offset
        )
        return questions
    except Exception as e:
        logger.error(f"Error getting questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get questions")

@router.get("/search", response_model=List[QuestionResponse])
async def search_questions(
    query: str,
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """Search questions by text"""
    try:
        questions = await question_service.search_questions(query, limit)
        return questions
    except Exception as e:
        logger.error(f"Error searching questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search questions")

@router.get("/{question_id}", response_model=QuestionDetailResponse)
async def get_question(
    question_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get question by ID (without answers)"""
    try:
        question = await question_service.get_question(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get question")

@router.get("/{question_id}/with-answers", response_model=QuestionWithAnswerResponse)
async def get_question_with_answers(
    question_id: str,
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Get question with answers (pro feature)"""
    try:
        question = await question_service.get_question_with_answers(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting question with answers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get question")

@router.post("/{question_id}/attempt", response_model=QuestionAttemptResponse)
async def attempt_question(
    question_id: str,
    attempt: QuestionAttemptCreate,
    current_user: User = Depends(get_current_user)
):
    """Submit an answer for a question"""
    try:
        result = await question_service.attempt_question(
            current_user.uid,
            question_id,
            attempt
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error attempting question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process attempt")

@router.get("/{question_id}/hint")
async def get_hint(
    question_id: str,
    hint_number: int = Query(1, ge=1, le=3),
    current_user: User = Depends(get_current_user)
):
    """Get a hint for a question"""
    try:
        hint = await question_service.get_hint(question_id, hint_number)
        if not hint:
            raise HTTPException(status_code=404, detail="Hint not found")
        return {"hint": hint}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting hint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get hint")

# Topics endpoints
@router.get("/topics/all", response_model=List[TopicResponse])
async def get_all_topics(
    subject: Optional[SubjectArea] = None,
    current_user: User = Depends(get_current_user)
):
    """Get all topics"""
    try:
        topics = await question_service.get_topics(subject)
        return topics
    except Exception as e:
        logger.error(f"Error getting topics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get topics")

@router.get("/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get topic by ID"""
    try:
        topic = await question_service.get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        return topic
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting topic: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get topic")

# Question Sets
@router.get("/sets/public", response_model=List[QuestionSetResponse])
async def get_public_sets(
    type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """Get public question sets"""
    try:
        sets = await question_service.get_public_sets(type, limit)
        return sets
    except Exception as e:
        logger.error(f"Error getting question sets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get question sets")

@router.get("/sets/{set_id}", response_model=QuestionSetDetailResponse)
async def get_question_set(
    set_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get question set by ID"""
    try:
        question_set = await question_service.get_question_set(set_id)
        if not question_set:
            raise HTTPException(status_code=404, detail="Question set not found")
        return question_set
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting question set: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get question set")

# Admin endpoints
@router.post("/", response_model=QuestionResponse)
async def create_question(
    question: QuestionCreate,
    admin: User = Depends(get_current_admin_user)
):
    """Create a new question (admin only)"""
    try:
        new_question = await question_service.create_question(
            question,
            admin.uid
        )
        logger.info(f"Question created: {new_question.question_id}")
        return new_question
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create question")

@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    question_update: QuestionUpdate,
    admin: User = Depends(get_current_admin_user)
):
    """Update a question (admin only)"""
    try:
        updated = await question_service.update_question(
            question_id,
            question_update.dict(exclude_unset=True),
            admin.uid
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Question not found")
        logger.info(f"Question updated: {question_id}")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update question")

@router.delete("/{question_id}")
async def delete_question(
    question_id: str,
    admin: User = Depends(get_current_admin_user)
):
    """Delete a question (admin only)"""
    try:
        success = await question_service.delete_question(question_id)
        if not success:
            raise HTTPException(status_code=404, detail="Question not found")
        logger.info(f"Question deleted: {question_id}")
        return {"message": "Question deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete question")

@router.post("/bulk")
async def bulk_create_questions(
    questions: List[QuestionCreate],
    admin: User = Depends(get_current_admin_user)
):
    """Bulk create questions (admin only)"""
    try:
        results = await question_service.bulk_create_questions(questions, admin.uid)
        logger.info(f"Bulk created {len(results)} questions")
        return {
            "message": f"Successfully created {len(results)} questions",
            "questions": results
        }
    except Exception as e:
        logger.error(f"Error bulk creating questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create questions")

@router.post("/sets", response_model=QuestionSetResponse)
async def create_question_set(
    name: str,
    description: Optional[str] = None,
    question_ids: List[str] = [],
    admin: User = Depends(get_current_admin_user)
):
    """Create a question set (admin only)"""
    try:
        question_set = await question_service.create_question_set(
            name,
            description,
            question_ids,
            admin.uid
        )
        logger.info(f"Question set created: {question_set.set_id}")
        return question_set
    except Exception as e:
        logger.error(f"Error creating question set: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create question set")

@router.post("/sets/{set_id}/questions")
async def add_questions_to_set(
    set_id: str,
    question_ids: List[str],
    admin: User = Depends(get_current_admin_user)
):
    """Add questions to a set (admin only)"""
    try:
        await question_service.add_questions_to_set(set_id, question_ids)
        logger.info(f"Questions added to set {set_id}")
        return {"message": "Questions added successfully"}
    except Exception as e:
        logger.error(f"Error adding questions to set: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add questions")

@router.delete("/sets/{set_id}/questions")
async def remove_questions_from_set(
    set_id: str,
    question_ids: List[str],
    admin: User = Depends(get_current_admin_user)
):
    """Remove questions from a set (admin only)"""
    try:
        await question_service.remove_questions_from_set(set_id, question_ids)
        logger.info(f"Questions removed from set {set_id}")
        return {"message": "Questions removed successfully"}
    except Exception as e:
        logger.error(f"Error removing questions from set: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove questions")