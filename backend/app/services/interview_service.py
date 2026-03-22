"""
Interview Service - Complete AI Interviewer business logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import random
import base64
import tempfile
import os
from uuid import uuid4

from app.core.database import firebase_client
from app.core.cache import cache_manager
from app.core.storage import storage_service
from app.ml_services.interview_ai import InterviewAI
from app.ml_services.voice_processor import VoiceProcessor
from app.ml_services.video_analyzer import VideoAnalyzer
from app.models.interview import (
    AIInterviewSession, InterviewType, InterviewStatus,
    InterviewDifficulty, InterviewMode, QuestionCategory,
    InterviewFeedback
)
from app.services.question_service import QuestionService

logger = logging.getLogger(__name__)

class InterviewService:
    """Interview service with complete business logic"""
    
    def __init__(self):
        self.interview_ai = InterviewAI()
        self.voice_processor = VoiceProcessor()
        self.video_analyzer = VideoAnalyzer()
        self.question_service = QuestionService()
    
    async def start_interview(self, user_id: str, setup: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new interview session"""
        
        # Validate setup
        await self._validate_setup(setup)
        
        # Generate questions based on setup
        questions = await self._generate_questions(user_id, setup)
        
        if not questions:
            raise ValueError("Could not generate questions for the specified criteria")
        
        # Create session
        session_id = str(uuid4())
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "interview_type": setup["interview_type"],
            "interview_mode": setup["interview_mode"],
            "status": InterviewStatus.IN_PROGRESS,
            "title": self._generate_title(setup),
            "description": setup.get("description"),
            "difficulty": setup["difficulty"],
            "duration_minutes": setup["duration_minutes"],
            "company_focus": setup.get("company_focus"),
            "role_focus": setup.get("role_focus"),
            "categories": setup.get("categories", []),
            "topics": setup.get("topics", []),
            "questions": questions,
            "total_questions": len(questions),
            "current_question_index": 0,
            "responses": [],
            "scores": {},
            "started_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "allow_follow_up": setup.get("allow_follow_up", True),
            "allow_hints": setup.get("allow_hints", True),
            "show_feedback_immediately": setup.get("show_feedback_immediately", False)
        }
        
        # Save session
        firebase_client.set_data(f"interview_sessions/{user_id}/{session_id}", session)
        
        # Get current question
        current_question = await self._prepare_question_for_client(
            questions[0],
            show_hint=False
        )
        
        return {
            **session,
            "current_question": current_question,
            "time_elapsed": 0,
            "time_remaining": setup["duration_minutes"] * 60
        }
    
    async def _validate_setup(self, setup: Dict[str, Any]):
        """Validate interview setup"""
        
        # Check if company focus exists
        if setup.get("company_focus"):
            companies = firebase_client.get_data("company_grids") or {}
            if setup["company_focus"] not in companies:
                raise ValueError(f"Company {setup['company_focus']} not found")
        
        # Validate duration
        if setup["duration_minutes"] not in [15, 30, 45, 60, 90, 120]:
            raise ValueError("Invalid duration")
    
    def _generate_title(self, setup: Dict[str, Any]) -> str:
        """Generate interview title"""
        
        if setup.get("company_focus"):
            return f"{setup['company_focus']} Interview Practice"
        elif setup.get("role_focus"):
            return f"{setup['role_focus']} Interview"
        elif setup["interview_mode"] == InterviewMode.MOCK:
            return "Mock Interview"
        elif setup["interview_mode"] == InterviewMode.ASSESSMENT:
            return "Skill Assessment"
        else:
            return f"{setup['difficulty'].capitalize()} Practice Interview"
    
    async def _generate_questions(self, user_id: str, setup: Dict[str, Any]) -> List[Dict]:
        """Generate interview questions based on setup"""
        
        questions = []
        
        # If company-specific, use company questions
        if setup.get("company_focus"):
            company_questions = await self._get_company_questions(
                setup["company_focus"],
                setup.get("role_focus"),
                setup["difficulty"]
            )
            questions.extend(company_questions)
        
        # Add behavioral questions
        behavioral_count = self._get_question_count(setup, QuestionCategory.BEHAVIORAL)
        if behavioral_count > 0:
            behavioral = await self._get_behavioral_questions(
                behavioral_count,
                setup["difficulty"]
            )
            questions.extend(behavioral)
        
        # Add technical questions
        technical_count = self._get_question_count(setup, QuestionCategory.TECHNICAL)
        if technical_count > 0:
            technical = await self._get_technical_questions(
                user_id,
                technical_count,
                setup["difficulty"],
                setup.get("topics")
            )
            questions.extend(technical)
        
        # Add system design if applicable
        if QuestionCategory.SYSTEM_DESIGN in setup.get("categories", []):
            design_count = self._get_question_count(setup, QuestionCategory.SYSTEM_DESIGN)
            if design_count > 0:
                design = await self._get_system_design_questions(
                    design_count,
                    setup["difficulty"]
                )
                questions.extend(design)
        
        # Add coding questions if applicable
        if QuestionCategory.CODING in setup.get("categories", []):
            coding_count = self._get_question_count(setup, QuestionCategory.CODING)
            if coding_count > 0:
                coding = await self._get_coding_questions(
                    coding_count,
                    setup["difficulty"]
                )
                questions.extend(coding)
        
        # Shuffle and limit to total questions
        random.shuffle(questions)
        total_needed = self._calculate_total_questions(setup)
        
        # Add IDs to questions
        for i, q in enumerate(questions[:total_needed]):
            q["question_id"] = str(uuid4())
            q["order"] = i
        
        return questions[:total_needed]
    
    def _get_question_count(self, setup: Dict[str, Any], category: QuestionCategory) -> int:
        """Get number of questions for a category"""
        
        if "categories" not in setup or not setup["categories"]:
            # Default distribution
            total = self._calculate_total_questions(setup)
            if category == QuestionCategory.BEHAVIORAL:
                return max(1, total // 4)
            elif category == QuestionCategory.TECHNICAL:
                return max(2, total // 2)
            elif category == QuestionCategory.SYSTEM_DESIGN:
                return max(1, total // 4)
            elif category == QuestionCategory.CODING:
                return max(1, total // 4)
            return 0
        
        # User specified categories
        category_counts = {}
        total_categories = len(setup["categories"])
        total_questions = self._calculate_total_questions(setup)
        
        # Equal distribution
        per_category = total_questions // total_categories
        remainder = total_questions % total_categories
        
        for i, cat in enumerate(setup["categories"]):
            category_counts[cat] = per_category + (1 if i < remainder else 0)
        
        return category_counts.get(category, 0)
    
    def _calculate_total_questions(self, setup: Dict[str, Any]) -> int:
        """Calculate total questions based on duration"""
        
        # Rough estimate: 2-3 minutes per question on average
        duration = setup["duration_minutes"]
        
        if duration <= 15:
            return 5
        elif duration <= 30:
            return 10
        elif duration <= 45:
            return 15
        elif duration <= 60:
            return 20
        elif duration <= 90:
            return 30
        else:
            return 40
    
    async def _get_company_questions(
        self,
        company: str,
        role: Optional[str],
        difficulty: InterviewDifficulty
    ) -> List[Dict]:
        """Get company-specific questions"""
        
        # Get company grid
        grid = firebase_client.get_data(f"company_grids/{company}")
        
        if not grid:
            return []
        
        question_ids = grid.get("question_ids", [])
        questions = []
        
        for qid in question_ids:
            question = await self.question_service.get_question_with_answers(qid)
            if question:
                # Convert to interview format
                questions.append({
                    "question_id": qid,
                    "category": QuestionCategory.TECHNICAL,
                    "difficulty": question.difficulty,
                    "question_text": question.title,
                    "context": question.description,
                    "expected_points": self._extract_expected_points(question),
                    "follow_up_questions": await self._generate_follow_ups(question),
                    "evaluation_criteria": self._create_evaluation_criteria(question),
                    "max_score": 10,
                    "hints": question.hints,
                    "references": question.references,
                    "company": company
                })
        
        # Filter by difficulty if specified
        if difficulty:
            questions = [q for q in questions if q["difficulty"] == difficulty]
        
        return questions
    
    async def _get_behavioral_questions(self, count: int, difficulty: InterviewDifficulty) -> List[Dict]:
        """Generate behavioral questions"""
        
        behavioral_db = [
            {
                "question_text": "Tell me about a time you faced a challenging technical problem. How did you approach it?",
                "context": "Use STAR method: Situation, Task, Action, Result",
                "expected_points": [
                    "Clear description of the situation",
                    "Specific actions taken",
                    "Quantifiable results",
                    "Learning and growth"
                ],
                "difficulty": InterviewDifficulty.BEGINNER
            },
            {
                "question_text": "Describe a situation where you had to work with a difficult team member. How did you handle it?",
                "context": "Focus on collaboration and conflict resolution",
                "expected_points": [
                    "Understanding different perspectives",
                    "Communication strategies used",
                    "Positive outcome achieved",
                    "Relationship maintained"
                ],
                "difficulty": InterviewDifficulty.INTERMEDIATE
            },
            {
                "question_text": "Tell me about a project that failed. What happened and what did you learn?",
                "context": "Show growth from failure",
                "expected_points": [
                    "Honest assessment of failure",
                    "Root cause analysis",
                    "Lessons learned",
                    "Application to future work"
                ],
                "difficulty": InterviewDifficulty.ADVANCED
            },
            {
                "question_text": "Describe a time you had to influence someone without authority. How did you do it?",
                "context": "Leadership without management",
                "expected_points": [
                    "Building consensus",
                    "Data-driven arguments",
                    "Stakeholder management",
                    "Successful outcome"
                ],
                "difficulty": InterviewDifficulty.ADVANCED
            },
            {
                "question_text": "Tell me about a time you had to make a decision with incomplete information. What was your process?",
                "context": "Decision-making under uncertainty",
                "expected_points": [
                    "Risk assessment",
                    "Gathering available data",
                    "Making assumptions explicit",
                    "Adjusting based on feedback"
                ],
                "difficulty": InterviewDifficulty.EXPERT
            }
        ]
        
        # Filter by difficulty
        filtered = [q for q in behavioral_db if q["difficulty"] == difficulty]
        
        # If not enough, include easier questions
        if len(filtered) < count:
            easier = [q for q in behavioral_db if q["difficulty"] in [InterviewDifficulty.BEGINNER, InterviewDifficulty.INTERMEDIATE]]
            filtered.extend(easier)
        
        # Add metadata
        for q in filtered:
            q["category"] = QuestionCategory.BEHAVIORAL
            q["question_id"] = str(uuid4())
            q["follow_up_questions"] = [
                "Can you elaborate on that?",
                "What was the outcome?",
                "What would you do differently?"
            ]
            q["evaluation_criteria"] = {
                "clarity": 3,
                "relevance": 3,
                "structure": 2,
                "impact": 2
            }
            q["max_score"] = 10
        
        return filtered[:count]
    
    async def _get_technical_questions(
        self,
        user_id: str,
        count: int,
        difficulty: InterviewDifficulty,
        topics: Optional[List[str]]
    ) -> List[Dict]:
        """Get technical questions based on user's level and topics"""
        
        # Get user's weak areas for personalized questions
        from app.services.analytics_service import AnalyticsService
        analytics = AnalyticsService()
        weak_topics = await analytics.get_weak_topics(user_id, 5)
        
        # Prioritize weak topics if specified
        focus_topics = []
        if weak_topics and topics:
            # Intersection of weak topics and requested topics
            weak_topic_names = [t["topic"] for t in weak_topics]
            focus_topics = [t for t in topics if t in weak_topic_names]
        
        # Get questions from database
        all_questions = firebase_client.get_data("questions") or {}
        
        questions = []
        for qid, question in all_questions.items():
            if question.get("status") != "approved":
                continue
            
            # Filter by difficulty
            if difficulty and question.get("difficulty") != difficulty:
                continue
            
            # Filter by topics
            if topics and question.get("topic") not in topics:
                continue
            
            # Prioritize focus topics
            if focus_topics and question.get("topic") in focus_topics:
                priority = 2
            elif weak_topics and question.get("topic") in [t["topic"] for t in weak_topics]:
                priority = 1
            else:
                priority = 0
            
            questions.append({
                "question_id": qid,
                "category": QuestionCategory.TECHNICAL,
                "difficulty": question.get("difficulty"),
                "question_text": question.get("title"),
                "context": question.get("description"),
                "expected_points": self._extract_expected_points(question),
                "follow_up_questions": await self._generate_follow_ups(question),
                "evaluation_criteria": self._create_evaluation_criteria(question),
                "max_score": 10,
                "hints": question.get("hints", []),
                "references": question.get("references", []),
                "topic": question.get("topic"),
                "priority": priority
            })
        
        # Sort by priority (higher first)
        questions.sort(key=lambda x: x["priority"], reverse=True)
        
        return questions[:count]
    
    def _extract_expected_points(self, question: Dict) -> List[str]:
        """Extract expected points from question"""
        
        points = []
        
        # From detailed explanation
        if question.get("detailed_explanation"):
            # Split into sentences
            sentences = question["detailed_explanation"].split('.')
            points = [s.strip() for s in sentences if len(s.strip()) > 20][:5]
        
        # From key points if available
        if question.get("key_points"):
            points = question["key_points"]
        
        # Default if none
        if not points:
            points = [
                "Understanding of core concepts",
                "Clear explanation",
                "Practical application",
                "Edge cases consideration",
                "Trade-offs discussion"
            ]
        
        return points
    
    async def _generate_follow_ups(self, question: Dict) -> List[str]:
        """Generate follow-up questions"""
        
        follow_ups = []
        
        # Use AI to generate follow-ups
        if question.get("type") == "system_design":
            follow_ups = [
                "How would you handle scaling?",
                "What are the trade-offs in your design?",
                "How would you monitor this system?"
            ]
        elif question.get("type") == "coding":
            follow_ups = [
                "What's the time complexity?",
                "How would you handle edge cases?",
                "Can you optimize further?"
            ]
        else:
            follow_ups = [
                "Can you provide an example?",
                "What alternatives exist?",
                "How does this compare to other approaches?"
            ]
        
        return follow_ups
    
    def _create_evaluation_criteria(self, question: Dict) -> Dict[str, float]:
        """Create evaluation criteria for question"""
        
        if question.get("type") == "system_design":
            return {
                "architecture": 3,
                "scalability": 2,
                "trade_offs": 2,
                "technology_choices": 2,
                "communication": 1
            }
        elif question.get("type") == "coding":
            return {
                "correctness": 3,
                "efficiency": 2,
                "code_quality": 2,
                "edge_cases": 2,
                "explanation": 1
            }
        else:
            return {
                "accuracy": 3,
                "depth": 2,
                "clarity": 2,
                "examples": 2,
                "structure": 1
            }
    
    async def _get_system_design_questions(self, count: int, difficulty: InterviewDifficulty) -> List[Dict]:
        """Get system design questions"""
        
        design_db = [
            {
                "question_text": "Design YouTube",
                "context": "Video streaming platform",
                "expected_points": [
                    "Video upload and processing",
                    "Content delivery network",
                    "Recommendation system",
                    "Scalability considerations"
                ],
                "difficulty": InterviewDifficulty.ADVANCED
            },
            {
                "question_text": "Design Twitter",
                "context": "Social media platform",
                "expected_points": [
                    "Feed generation",
                    "Real-time updates",
                    "Database sharding",
                    "Caching strategy"
                ],
                "difficulty": InterviewDifficulty.ADVANCED
            },
            {
                "question_text": "Design Uber",
                "context": "Ride-sharing platform",
                "expected_points": [
                    "Real-time location tracking",
                    "Matching algorithm",
                    "Payment processing",
                    "Fare calculation"
                ],
                "difficulty": InterviewDifficulty.ADVANCED
            },
            {
                "question_text": "Design a URL shortener",
                "context": "Like bit.ly",
                "expected_points": [
                    "Unique ID generation",
                    "Database design",
                    "Redirection",
                    "Analytics tracking"
                ],
                "difficulty": InterviewDifficulty.INTERMEDIATE
            },
            {
                "question_text": "Design a chat system",
                "context": "Real-time messaging",
                "expected_points": [
                    "WebSocket connections",
                    "Message persistence",
                    "Read receipts",
                    "Push notifications"
                ],
                "difficulty": InterviewDifficulty.INTERMEDIATE
            }
        ]
        
        # Filter by difficulty
        filtered = [q for q in design_db if q["difficulty"] == difficulty]
        
        if len(filtered) < count:
            filtered = design_db
        
        for q in filtered:
            q["category"] = QuestionCategory.SYSTEM_DESIGN
            q["question_id"] = str(uuid4())
            q["follow_up_questions"] = [
                "How would you handle scale?",
                "What are the bottlenecks?",
                "How would you make it fault-tolerant?"
            ]
            q["evaluation_criteria"] = {
                "architecture": 3,
                "scalability": 2,
                "trade_offs": 2,
                "details": 2,
                "communication": 1
            }
            q["max_score"] = 10
            q["hints"] = [
                "Think about the core components",
                "Consider data flow",
                "Address scaling challenges"
            ]
        
        return filtered[:count]
    
    async def _get_coding_questions(self, count: int, difficulty: InterviewDifficulty) -> List[Dict]:
        """Get coding questions"""
        
        coding_db = [
            {
                "question_text": "Implement a function to reverse a linked list",
                "context": "Data structures",
                "expected_points": [
                    "Iterative approach",
                    "Recursive approach",
                    "Time complexity O(n)",
                    "Space complexity O(1)"
                ],
                "difficulty": InterviewDifficulty.BEGINNER,
                "programming_language": "python",
                "code_snippet": "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverseList(head: ListNode) -> ListNode:\n    # Your code here\n    pass"
            },
            {
                "question_text": "Find the longest palindromic substring",
                "context": "String manipulation",
                "expected_points": [
                    "Expand around center approach",
                    "Dynamic programming approach",
                    "Handle even and odd length",
                    "Time complexity optimization"
                ],
                "difficulty": InterviewDifficulty.INTERMEDIATE,
                "programming_language": "python"
            },
            {
                "question_text": "Design a LRU cache",
                "context": "System design",
                "expected_points": [
                    "Use dictionary + doubly linked list",
                    "O(1) get and put operations",
                    "Handle capacity limit",
                    "Thread safety considerations"
                ],
                "difficulty": InterviewDifficulty.ADVANCED,
                "programming_language": "python"
            }
        ]
        
        # Filter by difficulty
        filtered = [q for q in coding_db if q["difficulty"] == difficulty]
        
        if len(filtered) < count:
            filtered = coding_db
        
        for q in filtered:
            q["category"] = QuestionCategory.CODING
            q["question_id"] = str(uuid4())
            q["follow_up_questions"] = [
                "What's the time complexity?",
                "How would you handle edge cases?",
                "Can you optimize further?"
            ]
            q["evaluation_criteria"] = {
                "correctness": 3,
                "efficiency": 2,
                "code_quality": 2,
                "edge_cases": 2,
                "explanation": 1
            }
            q["max_score"] = 10
            q["hints"] = [
                "Think about the data structure",
                "Consider the base case",
                "Optimize step by step"
            ]
        
        return filtered[:count]
    
    async def _prepare_question_for_client(self, question: Dict, show_hint: bool = False) -> Dict:
        """Prepare question for client (remove sensitive data)"""
        
        client_question = {
            "question_id": question["question_id"],
            "question_text": question["question_text"],
            "context": question.get("context"),
            "category": question["category"],
            "difficulty": question["difficulty"],
        }
        
        # Add type-specific fields
        if question.get("programming_language"):
            client_question["programming_language"] = question["programming_language"]
            client_question["code_snippet"] = question.get("code_snippet")
        
        if question.get("requirements"):
            client_question["requirements"] = question["requirements"]
        
        if question.get("constraints"):
            client_question["constraints"] = question["constraints"]
        
        # Add hint if allowed
        if show_hint and question.get("hints"):
            client_question["hint"] = question["hints"][0]
        
        return client_question
    
    async def get_session(self, session_id: str, user_id: str) -> Optional[Dict]:
        """Get interview session details"""
        
        session = firebase_client.get_data(f"interview_sessions/{user_id}/{session_id}")
        
        if not session:
            return None
        
        # Calculate elapsed time
        if session["status"] == InterviewStatus.IN_PROGRESS:
            started_at = datetime.fromisoformat(session["started_at"])
            elapsed = (datetime.utcnow() - started_at).seconds
            session["time_elapsed"] = elapsed
            session["time_remaining"] = max(0, session["duration_minutes"] * 60 - elapsed)
        
        # Get current question
        if session["status"] == InterviewStatus.IN_PROGRESS:
            current_idx = session["current_question_index"]
            if current_idx < len(session["questions"]):
                session["current_question"] = await self._prepare_question_for_client(
                    session["questions"][current_idx],
                    show_hint=False
                )
        
        return session
    
    async def pause_session(self, session_id: str, user_id: str):
        """Pause interview session"""
        
        session = firebase_client.get_data(f"interview_sessions/{user_id}/{session_id}")
        
        if not session:
            raise ValueError("Session not found")
        
        if session["status"] != InterviewStatus.IN_PROGRESS:
            raise ValueError("Session is not in progress")
        
        session["status"] = InterviewStatus.PAUSED
        session["paused_at"] = datetime.utcnow().isoformat()
        
        firebase_client.set_data(f"interview_sessions/{user_id}/{session_id}", session)
    
    async def resume_session(self, session_id: str, user_id: str) -> Dict:
        """Resume interview session"""
        
        session = firebase_client.get_data(f"interview_sessions/{user_id}/{session_id}")
        
        if not session:
            raise ValueError("Session not found")
        
        if session["status"] != InterviewStatus.PAUSED:
            raise ValueError("Session is not paused")
        
        # Adjust started_at to account for pause duration
        if session.get("paused_at"):
            paused_at = datetime.fromisoformat(session["paused_at"])
            started_at = datetime.fromisoformat(session["started_at"])
            pause_duration = (datetime.utcnow() - paused_at).seconds
            
            # Adjust started_at to maintain total duration
            session["started_at"] = (started_at - timedelta(seconds=pause_duration)).isoformat()
        
        session["status"] = InterviewStatus.IN_PROGRESS
        del session["paused_at"]
        
        firebase_client.set_data(f"interview_sessions/{user_id}/{session_id}", session)
        
        return await self.get_session(session_id, user_id)
    
    async def end_session(self, session_id: str, user_id: str) -> Dict:
        """End interview session and generate feedback"""
        
        session = firebase_client.get_data(f"interview_sessions/{user_id}/{session_id}")
        
        if not session:
            raise ValueError("Session not found")
        
        # Generate feedback
        feedback = await self._generate_feedback(session)
        
        # Update session
        session["status"] = InterviewStatus.COMPLETED
        session["completed_at"] = datetime.utcnow().isoformat()
        session["feedback"] = feedback.dict()
        session["scores"] = {
            "overall": feedback.overall_score,
            "technical": feedback.technical_score,
            "communication": feedback.communication_score,
            "problem_solving": feedback.problem_solving_score
        }
        
        firebase_client.set_data(f"interview_sessions/{user_id}/{session_id}", session)
        
        # Save feedback separately
        firebase_client.set_data(
            f"interview_feedback/{user_id}/{session_id}",
            feedback.dict()
        )
        
        return {
            "session_id": session_id,
            "completed": True,
            "feedback_ready": True,
            "overall_score": feedback.overall_score
        }
    
    async def get_current_question(self, session_id: str, user_id: str) -> Optional[Dict]:
        """Get current interview question"""
        
        session = await self.get_session(session_id, user_id)
        
        if not session:
            return None
        
        return session.get("current_question")
    
    async def submit_response(self, session_id: str, user_id: str, response_data: Dict) -> Dict:
        """Submit response to interview question"""
        
        # Get session
        session = firebase_client.get_data(f"interview_sessions/{user_id}/{session_id}")
        
        if not session:
            raise ValueError("Session not found")
        
        if session["status"] != InterviewStatus.IN_PROGRESS:
            raise ValueError("Session is not in progress")
        
        # Verify question
        question_id = response_data["question_id"]
        current_idx = session["current_question_index"]
        current_question = session["questions"][current_idx]
        
        if current_question["question_id"] != question_id:
            raise ValueError("Not the current question")
        
        # Process response
        response_id = str(uuid4())
        
        # Handle different response types
        if response_data.get("audio_base64"):
            # Process audio
            audio_url = await self._process_audio_response(
                response_data["audio_base64"],
                session_id,
                question_id,
                user_id
            )
            
            # Analyze voice
            voice_analysis = await self.voice_processor.analyze(
                audio_url,
                response_data.get("text_response", "")
            )
        else:
            voice_analysis = None
            audio_url = None
        
        if response_data.get("video_base64"):
            # Process video
            video_url = await self._process_video_response(
                response_data["video_base64"],
                session_id,
                question_id,
                user_id
            )
            
            # Analyze video
            video_analysis = await self.video_analyzer.analyze(video_url)
        else:
            video_analysis = None
            video_url = None
        
        # Analyze response with AI
        analysis = await self.interview_ai.analyze_response(
            question=current_question,
            response_text=response_data.get("text_response", ""),
            voice_analysis=voice_analysis,
            video_analysis=video_analysis
        )
        
        # Create response record
        response_record = {
            "response_id": response_id,
            "question_id": question_id,
            "user_id": user_id,
            "session_id": session_id,
            "text_response": response_data.get("text_response"),
            "audio_response_url": audio_url,
            "video_response_url": video_url,
            "time_taken_seconds": response_data["time_taken_seconds"],
            "hints_used": response_data.get("hints_used", 0),
            "created_at": datetime.utcnow().isoformat(),
            "analysis": analysis,
            "score": analysis.get("score", 0)
        }
        
        # Save response
        firebase_client.set_data(
            f"interview_responses/{user_id}/{session_id}/{response_id}",
            response_record
        )
        
        # Add to session
        session["responses"].append(response_record)
        
        # Move to next question or complete
        if current_idx + 1 < session["total_questions"]:
            session["current_question_index"] = current_idx + 1
            next_question = await self._prepare_question_for_client(
                session["questions"][current_idx + 1],
                show_hint=False
            )
            session_completed = False
        else:
            next_question = None
            session_completed = True
        
        # Save session
        firebase_client.set_data(f"interview_sessions/{user_id}/{session_id}", session)
        
        # Prepare result
        result = {
            "response_id": response_id,
            "question_id": question_id,
            "next_question": next_question,
            "session_completed": session_completed,
            "progress": {
                "current": session["current_question_index"] + 1 if not session_completed else session["total_questions"],
                "total": session["total_questions"]
            }
        }
        
        # Add immediate feedback if enabled
        if session.get("show_feedback_immediately"):
            result["feedback"] = {
                "score": analysis.get("score", 0),
                "feedback": analysis.get("feedback", ""),
                "strengths": analysis.get("strengths", []),
                "improvements": analysis.get("improvements", [])
            }
        
        return result
    
    async def _process_audio_response(self, audio_base64: str, session_id: str, question_id: str, user_id: str) -> str:
        """Process audio response and upload to storage"""
        
        # Decode base64
        audio_data = base64.b64decode(audio_base64)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name
        
        # Upload to storage
        storage_path = f"interview_audio/{user_id}/{session_id}/{question_id}_{datetime.utcnow().timestamp()}.webm"
        audio_url = await storage_service.upload_file(
            audio_data,
            storage_path,
            "audio/webm"
        )
        
        # Clean up
        os.unlink(tmp_path)
        
        return audio_url
    
    async def _process_video_response(self, video_base64: str, session_id: str, question_id: str, user_id: str) -> str:
        """Process video response and upload to storage"""
        
        # Decode base64
        video_data = base64.b64decode(video_base64)
        
        # Upload to storage
        storage_path = f"interview_video/{user_id}/{session_id}/{question_id}_{datetime.utcnow().timestamp()}.webm"
        video_url = await storage_service.upload_file(
            video_data,
            storage_path,
            "video/webm"
        )
        
        return video_url
    
    async def get_hint(self, session_id: str, user_id: str, question_id: str) -> str:
        """Get hint for current question"""
        
        session = firebase_client.get_data(f"interview_sessions/{user_id}/{session_id}")
        
        if not session:
            raise ValueError("Session not found")
        
        # Find question
        for question in session["questions"]:
            if question["question_id"] == question_id:
                hints = question.get("hints", [])
                
                # Track hint usage
                hint_used = {
                    "question_id": question_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "hint_index": 0
                }
                
                # Add to session tracking
                if "hints_used" not in session:
                    session["hints_used"] = []
                session["hints_used"].append(hint_used)
                
                firebase_client.set_data(f"interview_sessions/{user_id}/{session_id}", session)
                
                return hints[0] if hints else "No hints available for this question."
        
        raise ValueError("Question not found")
    
    async def get_feedback(self, session_id: str, user_id: str, include_detailed: bool) -> Optional[Dict]:
        """Get interview feedback"""
        
        # Try to get existing feedback
        feedback = firebase_client.get_data(f"interview_feedback/{user_id}/{session_id}")
        
        if not feedback:
            # Generate feedback if not exists
            session = firebase_client.get_data(f"interview_sessions/{user_id}/{session_id}")
            if session and session.get("status") == InterviewStatus.COMPLETED:
                feedback_obj = await self._generate_feedback(session)
                feedback = feedback_obj.dict()
                
                # Save for future
                firebase_client.set_data(f"interview_feedback/{user_id}/{session_id}", feedback)
            else:
                return None
        
        if not include_detailed:
            # Remove detailed analysis
            feedback.pop("question_feedback", None)
            feedback.pop("transcript", None)
        
        return feedback
    
    async def _generate_feedback(self, session: Dict) -> InterviewFeedback:
        """Generate comprehensive interview feedback"""
        
        responses = session.get("responses", [])
        questions = session.get("questions", [])
        
        if not responses:
            return InterviewFeedback(
                session_id=session["session_id"],
                user_id=session["user_id"],
                overall_score=0,
                technical_score=0,
                communication_score=0,
                problem_solving_score=0,
                category_scores={},
                strengths=["No responses recorded"],
                weaknesses=["Complete the interview to receive feedback"],
                improvements=["Practice with more questions"],
                question_feedback=[],
                recommended_topics=["Start with basic topics"]
            )
        
        # Calculate scores
        total_score = 0
        category_scores = {}
        question_feedback = []
        
        for response in responses:
            question_id = response["question_id"]
            question = next((q for q in questions if q["question_id"] == question_id), None)
            
            if question:
                score = response.get("score", 0)
                total_score += score
                
                category = question.get("category")
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(score)
                
                question_feedback.append({
                    "question_id": question_id,
                    "question_text": question.get("question_text"),
                    "score": score,
                    "feedback": response.get("analysis", {}).get("feedback", ""),
                    "strengths": response.get("analysis", {}).get("strengths", []),
                    "improvements": response.get("analysis", {}).get("improvements", [])
                })
        
        # Average scores
        avg_score = total_score / len(responses) if responses else 0
        
        # Category averages
        avg_category_scores = {}
        for category, scores in category_scores.items():
            avg_category_scores[category] = sum(scores) / len(scores)
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for qf in question_feedback:
            if qf["score"] >= 8:
                strengths.append(f"Strong performance on {qf['question_text'][:50]}...")
            elif qf["score"] <= 5:
                weaknesses.append(f"Need improvement on {qf['question_text'][:50]}...")
        
        # Generate improvements
        improvements = []
        for w in weaknesses[:3]:
            improvements.append(f"Focus on: {w}")
        
        # Generate recommended topics
        recommended_topics = []
        for category, score in avg_category_scores.items():
            if score < 7:
                recommended_topics.append(f"Improve {category} skills")
        
        return InterviewFeedback(
            session_id=session["session_id"],
            user_id=session["user_id"],
            overall_score=round(avg_score, 2),
            technical_score=round(avg_category_scores.get(QuestionCategory.TECHNICAL, 0), 2),
            communication_score=round(avg_category_scores.get(QuestionCategory.BEHAVIORAL, 0), 2),
            problem_solving_score=round(
                (avg_category_scores.get(QuestionCategory.SYSTEM_DESIGN, 0) +
                 avg_category_scores.get(QuestionCategory.CODING, 0)) / 2, 2
            ),
            category_scores=avg_category_scores,
            strengths=strengths[:5],
            weaknesses=weaknesses[:5],
            improvements=improvements[:5],
            question_feedback=question_feedback,
            recommended_topics=recommended_topics[:5],
            resources=[],
            created_at=datetime.utcnow()
        )
    
    async def get_templates(self, mode: Optional[InterviewMode], company: Optional[str]) -> List[Dict]:
        """Get interview templates"""
        
        templates = firebase_client.get_data("interview_templates") or {}
        
        result = []
        for tid, template in templates.items():
            if template.get("is_active", True):
                if mode and template.get("interview_mode") != mode:
                    continue
                if company and template.get("company") != company:
                    continue
                result.append(template)
        
        return result
    
    async def get_template(self, template_id: str) -> Optional[Dict]:
        """Get interview template by ID"""
        
        return firebase_client.get_data(f"interview_templates/{template_id}")
    
    async def start_company_interview(
        self,
        user_id: str,
        company: str,
        role: Optional[str],
        difficulty: InterviewDifficulty
    ) -> Dict:
        """Start company-specific interview"""
        
        # Create setup based on company
        setup = {
            "interview_type": InterviewType.MIXED,
            "interview_mode": InterviewMode.COMPANY_SPECIFIC,
            "difficulty": difficulty,
            "duration_minutes": 60,
            "company_focus": company,
            "role_focus": role,
            "categories": [
                QuestionCategory.TECHNICAL,
                QuestionCategory.BEHAVIORAL,
                QuestionCategory.SYSTEM_DESIGN
            ],
            "topics": [],
            "allow_follow_up": True,
            "allow_hints": True,
            "show_feedback_immediately": False
        }
        
        return await self.start_interview(user_id, setup)
    
    async def get_history(self, user_id: str, limit: int) -> List[Dict]:
        """Get user's interview history"""
        
        sessions = firebase_client.get_data(f"interview_sessions/{user_id}") or {}
        
        history = []
        for session_id, session in sessions.items():
            if session.get("status") == InterviewStatus.COMPLETED:
                history.append({
                    "session_id": session_id,
                    "title": session.get("title"),
                    "interview_type": session.get("interview_type"),
                    "interview_mode": session.get("interview_mode"),
                    "difficulty": session.get("difficulty"),
                    "company_focus": session.get("company_focus"),
                    "completed_at": session.get("completed_at"),
                    "overall_score": session.get("scores", {}).get("overall"),
                    "duration_minutes": session.get("duration_minutes")
                })
        
        # Sort by completed_at desc
        history.sort(key=lambda x: x["completed_at"] if x["completed_at"] else "", reverse=True)
        
        return history[:limit]
    
    async def get_voice_analysis(self, response_id: str, user_id: str) -> Optional[Dict]:
        """Get voice analysis for a response"""
        
        # Find response
        sessions = firebase_client.get_data(f"interview_responses/{user_id}") or {}
        
        for session_id, responses in sessions.items():
            if response_id in responses:
                response = responses[response_id]
                return response.get("analysis", {}).get("voice_analysis")
        
        return None
    
    async def get_video_analysis(self, response_id: str, user_id: str) -> Optional[Dict]:
        """Get video analysis for a response"""
        
        # Find response
        sessions = firebase_client.get_data(f"interview_responses/{user_id}") or {}
        
        for session_id, responses in sessions.items():
            if response_id in responses:
                response = responses[response_id]
                return response.get("analysis", {}).get("video_analysis")
        
        return None
    
    async def create_template(self, template_data: Dict[str, Any], created_by: str) -> Dict:
        """Create interview template (admin)"""
        
        template_id = str(uuid4())
        
        template = {
            "template_id": template_id,
            "name": template_data["name"],
            "description": template_data.get("description", ""),
            "interview_mode": template_data["interview_mode"],
            "difficulty": template_data["difficulty"],
            "company": template_data.get("company"),
            "role": template_data.get("role"),
            "category_distribution": template_data.get("category_distribution", {}),
            "total_questions": template_data.get("total_questions", 10),
            "default_duration": template_data.get("default_duration", 30),
            "question_pool": template_data.get("question_pool", []),
            "created_at": datetime.utcnow().isoformat(),
            "created_by": created_by,
            "is_active": True
        }
        
        firebase_client.set_data(f"interview_templates/{template_id}", template)
        
        return template
    
    async def update_template(self, template_id: str, template_data: Dict[str, Any], updated_by: str) -> Dict:
        """Update interview template (admin)"""
        
        template = firebase_client.get_data(f"interview_templates/{template_id}")
        
        if not template:
            raise ValueError("Template not found")
        
        template.update(template_data)
        template["updated_at"] = datetime.utcnow().isoformat()
        template["updated_by"] = updated_by
        
        firebase_client.set_data(f"interview_templates/{template_id}", template)
        
        return template
    
    # WebSocket real-time methods
    async def handle_realtime_response(self, session_id: str, user_id: str, message: Dict) -> Dict:
        """Handle real-time response via WebSocket"""
        
        # Similar to submit_response but optimized for real-time
        response_data = {
            "question_id": message["question_id"],
            "text_response": message.get("text"),
            "audio_base64": message.get("audio"),
            "time_taken_seconds": message.get("time_taken", 0),
            "hints_used": message.get("hints_used", 0)
        }
        
        return await self.submit_response(session_id, user_id, response_data)
    
    async def get_next_question_realtime(self, session_id: str, user_id: str) -> Optional[Dict]:
        """Get next question for real-time session"""
        
        session = await self.get_session(session_id, user_id)
        
        if session and session.get("current_question"):
            return session["current_question"]
        
        return None
    
    async def get_hint_realtime(self, session_id: str, user_id: str, question_id: str) -> str:
        """Get hint in real-time"""
        
        return await self.get_hint(session_id, user_id, question_id)
    
    async def end_session_realtime(self, session_id: str, user_id: str) -> Dict:
        """End session in real-time and get feedback"""
        
        result = await self.end_session(session_id, user_id)
        
        if result.get("feedback_ready"):
            feedback = await self.get_feedback(session_id, user_id, True)
            return {
                "session_completed": True,
                "feedback": feedback
            }
        
        return result