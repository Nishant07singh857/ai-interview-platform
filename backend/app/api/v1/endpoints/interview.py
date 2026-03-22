"""
Interview Endpoints - Complete AI Interviewer API
"""

from fastapi import APIRouter, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from typing import Optional, List, Dict, Any 
import logging
import json
from app.models.interview import (
    InterviewType, 
    InterviewStatus, 
    InterviewDifficulty, 
    InterviewMode,  # ✅ यह add करो
    QuestionCategory
)
from app.core.deps import get_current_user, get_current_admin_user, get_current_pro_user, get_current_user_optional
from app.models.user import User
from app.schemas.interview import (
    InterviewSetupRequest, InterviewResponseSubmission, InterviewAction,
    InterviewFeedbackRequest, InterviewSessionResponse, InterviewQuestionResponse,
    InterviewResponseResult, InterviewFeedbackResponse, InterviewTemplateResponse,
    InterviewHistoryResponse, VoiceAnalysisResponse, VideoAnalysisResponse,
)
from app.services.interview_service import InterviewService
from app.services.websocket_manager import websocket_manager

router = APIRouter(prefix="/interview", tags=["AI Interviewer"])
logger = logging.getLogger(__name__)
interview_service = InterviewService()

# Interview session management
@router.post("/sessions/start", response_model=InterviewSessionResponse)
async def start_interview(
    setup: InterviewSetupRequest,
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Start a new AI interview session (pro feature)"""
    try:
        session = await interview_service.start_interview(
            current_user.uid,
            setup.dict()
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting interview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start interview")

@router.get("/sessions/{session_id}", response_model=InterviewSessionResponse)
async def get_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get interview session details"""
    try:
        session = await interview_service.get_session(session_id, current_user.uid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get session")

@router.post("/sessions/{session_id}/pause")
async def pause_interview(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Pause interview session"""
    try:
        await interview_service.pause_session(session_id, current_user.uid)
        return {"message": "Interview paused"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error pausing interview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to pause interview")

@router.post("/sessions/{session_id}/resume", response_model=InterviewSessionResponse)
async def resume_interview(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Resume interview session"""
    try:
        session = await interview_service.resume_session(session_id, current_user.uid)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error resuming interview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resume interview")

@router.post("/sessions/{session_id}/end")
async def end_interview(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """End interview session"""
    try:
        result = await interview_service.end_session(session_id, current_user.uid)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error ending interview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end interview")

# Questions and responses
@router.get("/sessions/{session_id}/current-question", response_model=InterviewQuestionResponse)
async def get_current_question(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get current interview question"""
    try:
        question = await interview_service.get_current_question(session_id, current_user.uid)
        if not question:
            raise HTTPException(status_code=404, detail="No current question")
        return question
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get current question")

@router.post("/sessions/{session_id}/respond", response_model=InterviewResponseResult)
async def submit_response(
    session_id: str,
    response: InterviewResponseSubmission,
    current_user: User = Depends(get_current_user)
):
    """Submit response to interview question"""
    try:
        if response.session_id != session_id:
            raise HTTPException(status_code=400, detail="Session ID mismatch")
        
        result = await interview_service.submit_response(
            session_id,
            current_user.uid,
            response.dict()
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting response: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit response")

@router.get("/sessions/{session_id}/question/{question_id}/hint")
async def get_hint(
    session_id: str,
    question_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get hint for current question"""
    try:
        hint = await interview_service.get_hint(session_id, current_user.uid, question_id)
        return {"hint": hint}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting hint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get hint")

# Feedback
@router.get("/sessions/{session_id}/feedback", response_model=InterviewFeedbackResponse)
async def get_interview_feedback(
    session_id: str,
    include_detailed: bool = Query(False),
    current_user: User = Depends(get_current_pro_user)
):
    """Get comprehensive interview feedback (pro feature)"""
    try:
        feedback = await interview_service.get_feedback(
            session_id,
            current_user.uid,
            include_detailed
        )
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return feedback
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get feedback")

# Templates
@router.get("/templates", response_model=List[InterviewTemplateResponse])
async def get_interview_templates(
    mode: Optional[InterviewMode] = None,
    company: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get available interview templates"""
    try:
        templates = await interview_service.get_templates(
            mode=mode,
            company=company
        )
        return templates
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get templates")

@router.get("/templates/{template_id}", response_model=InterviewTemplateResponse)
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get interview template details"""
    try:
        template = await interview_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get template")

# Company-specific interviews
@router.post("/company/{company}/start", response_model=InterviewSessionResponse)
async def start_company_interview(
    company: str,
    role: Optional[str] = None,
    difficulty: InterviewDifficulty = InterviewDifficulty.INTERMEDIATE,
    current_user: User = Depends(get_current_pro_user)
):
    """Start company-specific interview (pro feature)"""
    try:
        session = await interview_service.start_company_interview(
            current_user.uid,
            company,
            role,
            difficulty
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting company interview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start company interview")

# History
@router.get("/history", response_model=List[InterviewHistoryResponse])
async def get_interview_history(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """Get user's interview history"""
    try:
        history = await interview_service.get_history(current_user.uid, limit)
        return history
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get history")

# Analysis endpoints
@router.get("/analysis/voice/{response_id}", response_model=VoiceAnalysisResponse)
async def analyze_voice(
    response_id: str,
    current_user: User = Depends(get_current_pro_user)
):
    """Get voice analysis for a response (pro feature)"""
    try:
        analysis = await interview_service.get_voice_analysis(response_id, current_user.uid)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voice analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get voice analysis")

@router.get("/analysis/video/{response_id}", response_model=VideoAnalysisResponse)
async def analyze_video(
    response_id: str,
    current_user: User = Depends(get_current_pro_user)
):
    """Get video analysis for a response (pro feature)"""
    try:
        analysis = await interview_service.get_video_analysis(response_id, current_user.uid)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get video analysis")

# Admin endpoints
@router.post("/templates", response_model=InterviewTemplateResponse)
async def create_template(
    template_data: Dict[str, Any],
    admin: User = Depends(get_current_admin_user)
):
    """Create interview template (admin only)"""
    try:
        template = await interview_service.create_template(template_data, admin.uid)
        return template
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create template")

@router.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    template_data: Dict[str, Any],
    admin: User = Depends(get_current_admin_user)
):
    """Update interview template (admin only)"""
    try:
        result = await interview_service.update_template(template_id, template_data, admin.uid)
        return result
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update template")

# WebSocket for real-time interviews
@router.websocket("/ws/{session_id}")
async def websocket_interview(
    websocket: WebSocket,
    session_id: str,
    token: str
):
    """WebSocket connection for real-time interview"""
    await websocket_manager.connect(websocket, session_id)
    
    try:
        # Authenticate user
        user = await get_current_user_ws(token)
        if not user:
            await websocket.send_json({"error": "Authentication failed"})
            await websocket.close()
            return
        
        # Join interview session
        await websocket_manager.join_session(session_id, websocket)
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Connected to interview session"
        })
        
        # Handle messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "response":
                # Handle voice/text response
                result = await interview_service.handle_realtime_response(
                    session_id,
                    user.uid,
                    message
                )
                await websocket.send_json({
                    "type": "feedback",
                    "data": result
                })
            
            elif message["type"] == "next":
                # Get next question
                question = await interview_service.get_next_question_realtime(
                    session_id,
                    user.uid
                )
                await websocket.send_json({
                    "type": "question",
                    "data": question
                })
            
            elif message["type"] == "hint":
                # Get hint
                hint = await interview_service.get_hint_realtime(
                    session_id,
                    user.uid,
                    message.get("question_id")
                )
                await websocket.send_json({
                    "type": "hint",
                    "data": {"hint": hint}
                })
            
            elif message["type"] == "end":
                # End session
                feedback = await interview_service.end_session_realtime(
                    session_id,
                    user.uid
                )
                await websocket.send_json({
                    "type": "feedback_complete",
                    "data": feedback
                })
                break
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        websocket_manager.disconnect(websocket, session_id)
        await websocket.close()