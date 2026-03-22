"""
Practice Service - Complete practice module business logic with Gemini integration
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import random
from uuid import uuid4

from app.core.database import firebase_client
from app.core.cache import cache_manager
from app.models.practice import PracticeType, SessionStatus
from app.models.question import Question
from app.services.question_service import QuestionService
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)
question_service = QuestionService()

class PracticeService:
    """Practice service with complete business logic"""
    
    async def start_quick_quiz(self, user_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start a quick quiz session"""
        
        # Get random questions
        questions = await self._get_random_questions(
            total=config.get("total_questions", 5),
            subjects=config.get("subjects"),
            difficulties=config.get("difficulties")
        )
        
        if not questions:
            raise ValueError("No questions available")
        
        # Create session
        session_id = str(uuid4())
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "type": PracticeType.QUICK_QUIZ,
            "status": SessionStatus.IN_PROGRESS,
            "title": "Quick Quiz",
            "total_questions": len(questions),
            "time_limit": config.get("time_limit", 5) * 60,
            "question_ids": [q["question_id"] for q in questions],
            "questions": self._initialize_questions(questions, config.get("shuffle", True)),
            "created_at": datetime.utcnow().isoformat(),
            "started_at": datetime.utcnow().isoformat(),
            "last_activity_at": datetime.utcnow().isoformat(),
            "current_question_index": 0,
            "questions_answered": 0,
            "correct_answers": 0,
            "incorrect_answers": 0,
            "time_per_question": []
        }
        
        # Save session
        firebase_client.set_data(f"practice_sessions/{user_id}/{session_id}", session)
        
        # Get current question
        current_question = await self._get_question_for_session(
            questions[0]["question_id"],
            session["questions"][questions[0]["question_id"]]
        )
        
        return {
            **session,
            "current_question": current_question,
            "time_elapsed": 0,
            "time_remaining": session["time_limit"]
        }
    
    async def start_topic_practice(self, user_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start topic-wise practice session with Gemini fallback"""
        
        logger.info(f"🎯 Starting topic practice for user {user_id}: {config}")
        
        # Get questions for topic (with Gemini generation if needed)
        questions = await self._get_questions_for_topic(
            subject=config["subject"],
            topic=config["topic"],
            subtopics=config.get("subtopics"),
            total=config.get("total_questions", 10),
            difficulty=config.get("difficulty"),
            user_id=user_id
        )
        
        if not questions:
            # If still no questions, generate with Gemini
            logger.info(f"📝 No questions found, generating with Gemini for {config['topic']}")
            questions = await gemini_service.generate_questions_for_topic(
                subject=config["subject"],
                topic=config["topic"],
                count=config.get("total_questions", 10),
                difficulty=config.get("difficulty")
            )
            
            # Save generated questions to database
            if questions:
                await self._save_questions_to_db(questions, config["subject"], config["topic"], user_id)
        
        if not questions:
            raise ValueError(f"Could not generate questions for topic {config['topic']}")
        
        # Create session
        session_id = str(uuid4())
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "type": PracticeType.TOPIC_WISE,
            "status": SessionStatus.IN_PROGRESS,
            "title": f"{config['topic']} Practice",
            "description": f"Practice {config['topic']} questions",
            "subject": config["subject"],
            "topic": config["topic"],
            "subtopics": config.get("subtopics"),
            "total_questions": len(questions),
            "time_limit": config.get("time_limit", 10) * 60,
            "question_ids": [q["question_id"] for q in questions],
            "questions": self._initialize_questions(questions, config.get("shuffle", True)),
            "created_at": datetime.utcnow().isoformat(),
            "started_at": datetime.utcnow().isoformat(),
            "last_activity_at": datetime.utcnow().isoformat(),
            "current_question_index": 0,
            "questions_answered": 0,
            "correct_answers": 0,
            "incorrect_answers": 0,
            "time_per_question": []
        }
        
        # Save session
        firebase_client.set_data(f"practice_sessions/{user_id}/{session_id}", session)
        
        # Get current question
        current_question = await self._get_question_for_session(
            questions[0]["question_id"],
            session["questions"][questions[0]["question_id"]]
        )
        
        return {
            **session,
            "current_question": current_question,
            "time_elapsed": 0,
            "time_remaining": session["time_limit"]
        }
    
    async def start_mock_test(self, user_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start a mock test session"""
        
        # Get questions based on configuration
        questions = await self._get_mock_test_questions(config)
        
        if not questions:
            raise ValueError("No questions available for mock test")
        
        # Create session
        session_id = str(uuid4())
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "type": PracticeType.MOCK_TEST,
            "status": SessionStatus.IN_PROGRESS,
            "title": config.get("title", f"{config['subject']} Mock Test"),
            "description": f"Comprehensive mock test for {config['subject']}",
            "subject": config["subject"],
            "total_questions": len(questions),
            "time_limit": config.get("time_limit", 30) * 60,
            "passing_score": config.get("passing_score", 70),
            "question_ids": [q["question_id"] for q in questions],
            "questions": self._initialize_questions(questions, shuffle=True),
            "created_at": datetime.utcnow().isoformat(),
            "started_at": datetime.utcnow().isoformat(),
            "last_activity_at": datetime.utcnow().isoformat(),
            "current_question_index": 0,
            "questions_answered": 0,
            "correct_answers": 0,
            "incorrect_answers": 0,
            "time_per_question": []
        }
        
        # Save session
        firebase_client.set_data(f"practice_sessions/{user_id}/{session_id}", session)
        
        # Get current question
        current_question = await self._get_question_for_session(
            questions[0]["question_id"],
            session["questions"][questions[0]["question_id"]]
        )
        
        return {
            **session,
            "current_question": current_question,
            "time_elapsed": 0,
            "time_remaining": session["time_limit"]
        }
    
    async def start_company_practice(self, user_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start company-specific practice session"""
        
        # Get company-specific questions
        questions = await self._get_company_questions(
            company=config["company"],
            role=config.get("role"),
            total=config.get("total_questions", 20),
            difficulty_focus=config.get("difficulty_focus")
        )
        
        if not questions:
            raise ValueError(f"No questions available for {config['company']}")
        
        # Create session
        session_id = str(uuid4())
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "type": PracticeType.COMPANY_GRID,
            "status": SessionStatus.IN_PROGRESS,
            "title": f"{config['company']} Interview Practice",
            "description": f"Practice questions commonly asked at {config['company']}",
            "company": config["company"],
            "role": config.get("role"),
            "total_questions": len(questions),
            "time_limit": config.get("time_limit", 25) * 60,
            "question_ids": [q["question_id"] for q in questions],
            "questions": self._initialize_questions(questions, shuffle=True),
            "created_at": datetime.utcnow().isoformat(),
            "started_at": datetime.utcnow().isoformat(),
            "last_activity_at": datetime.utcnow().isoformat(),
            "current_question_index": 0,
            "questions_answered": 0,
            "correct_answers": 0,
            "incorrect_answers": 0,
            "time_per_question": []
        }
        
        # Save session
        firebase_client.set_data(f"practice_sessions/{user_id}/{session_id}", session)
        
        # Get current question
        current_question = await self._get_question_for_session(
            questions[0]["question_id"],
            session["questions"][questions[0]["question_id"]]
        )
        
        return {
            **session,
            "current_question": current_question,
            "time_elapsed": 0,
            "time_remaining": session["time_limit"]
        }
    
    async def _get_questions_for_topic(
        self,
        subject: str,
        topic: str,
        subtopics: Optional[List[str]],
        total: int,
        difficulty: Optional[str],
        user_id: str
    ) -> List[Dict]:
        """Get questions for topic, try database first then Gemini"""
        
        # Try to get from database first
        questions = await self._get_questions_from_db(
            subject=subject,
            topic=topic,
            subtopics=subtopics,
            difficulty=difficulty
        )
        
        # If we have enough questions, return them
        if len(questions) >= total:
            logger.info(f"✅ Found {len(questions)} questions in database for {topic}")
            return questions[:total]
        
        # Not enough questions, generate with Gemini
        needed = total - len(questions)
        logger.info(f"⚠️ Only {len(questions)} questions in DB, generating {needed} new ones with Gemini")
        
        new_questions = await gemini_service.generate_questions_for_topic(
            subject=subject,
            topic=topic,
            count=needed,
            difficulty=difficulty
        )
        
        # Save new questions to database
        if new_questions:
            saved_ids = await self._save_questions_to_db(new_questions, subject, topic, user_id)
            
            # Convert saved questions to format expected by practice session
            for idx, q_data in enumerate(new_questions):
                questions.append({
                    "question_id": saved_ids[idx] if idx < len(saved_ids) else str(uuid4()),
                    "title": q_data.get("title", f"Question about {topic}"),
                    "description": q_data.get("description", ""),
                    "options": q_data.get("options", []),
                    "explanation": q_data.get("explanation", ""),
                    "difficulty": q_data.get("difficulty", difficulty or "medium"),
                    "type": "mcq"
                })
        
        return questions[:total]
    
    async def _get_questions_from_db(
        self,
        subject: str,
        topic: str,
        subtopics: Optional[List[str]],
        difficulty: Optional[str]
    ) -> List[Dict]:
        """Get approved questions from database"""
        
        all_questions = firebase_client.get_data("questions") or {}
        
        filtered = []
        for qid, question in all_questions.items():
            if question.get("status") != "approved":
                continue
            
            if question.get("subject") != subject:
                continue
            
            if question.get("topic") != topic:
                continue
            
            if subtopics and question.get("subtopic") not in subtopics:
                continue
            
            if difficulty and question.get("difficulty") != difficulty:
                continue
            
            filtered.append({
                "question_id": qid,
                "title": question.get("title"),
                "description": question.get("description"),
                "options": question.get("options", []),
                "explanation": question.get("explanation"),
                "difficulty": question.get("difficulty"),
                "type": question.get("type", "mcq")
            })
        
        # Randomize order
        random.shuffle(filtered)
        return filtered
    
    async def _save_questions_to_db(
        self,
        questions: List[Dict],
        subject: str,
        topic: str,
        user_id: str
    ) -> List[str]:
        """Save generated questions to database"""
        
        saved_ids = []
        for q_data in questions:
            question_id = str(uuid4())
            
            # Prepare question for database
            question_record = {
                "question_id": question_id,
                "subject": subject,
                "topic": topic,
                "subtopic": q_data.get("subtopic"),
                "title": q_data.get("title", f"Question about {topic}"),
                "description": q_data.get("description", ""),
                "options": q_data.get("options", []),
                "correct_answers": self._extract_correct_answers(q_data),
                "explanation": q_data.get("explanation", ""),
                "difficulty": q_data.get("difficulty", "medium"),
                "type": q_data.get("type", "mcq"),
                "tags": q_data.get("tags", []),
                "status": "approved",  # Auto-approve generated questions
                "created_by": "gemini",
                "created_for_user": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "times_used": 0,
                "times_correct": 0,
                "correct_rate": 0.0
            }
            
            # Save to database
            firebase_client.set_data(f"questions/{question_id}", question_record)
            saved_ids.append(question_id)
            
            # Update question count for topic
            await self._update_topic_question_count(subject, topic)
        
        logger.info(f"✅ Saved {len(saved_ids)} questions to database for {subject} - {topic}")
        return saved_ids
    
    def _extract_correct_answers(self, question: Dict) -> List[str]:
        """Extract correct answer IDs from question"""
        
        correct = []
        for opt in question.get("options", []):
            if opt.get("is_correct"):
                correct.append(opt.get("id"))
        return correct
    
    async def _update_topic_question_count(self, subject: str, topic: str):
        """Update question count for topic in database"""
        
        topics_ref = firebase_client.get_reference(f"topics/{subject}")
        topics = topics_ref.get() or []
        
        if topic not in topics:
            topics.append(topic)
            topics_ref.set(topics)
            logger.info(f"📚 Added new topic '{topic}' to {subject}")
    
    def _initialize_questions(self, questions: List[Dict], shuffle: bool) -> Dict:
        """Initialize questions for session"""
        
        if shuffle:
            random.shuffle(questions)
        
        questions_dict = {}
        for idx, q in enumerate(questions):
            questions_dict[q["question_id"]] = {
                "order": idx,
                "status": "pending",
                "answer": None,
                "is_correct": None,
                "time_taken": None,
                "hints_used": 0
            }
        
        return questions_dict
    
    async def _get_question_for_session(self, question_id: str, status: Dict) -> Dict:
        """Get question data for session display"""
        
        question = firebase_client.get_data(f"questions/{question_id}")
        
        if question:
            return {
                "question_id": question_id,
                "order": status["order"],
                "title": question.get("title"),
                "description": question.get("description"),
                "type": question.get("type"),
                "difficulty": question.get("difficulty"),
                "options": question.get("options", []),
                "code_snippet": question.get("code_snippet"),
                "time_limit": question.get("time_limit")
            }
        
        return None
    
    async def get_session(self, session_id: str, user_id: str) -> Optional[Dict]:
        """Get practice session details"""
        
        session = firebase_client.get_data(f"practice_sessions/{user_id}/{session_id}")
        
        if not session:
            return None
        
        # Calculate elapsed time
        if session["status"] == SessionStatus.IN_PROGRESS:
            started_at = datetime.fromisoformat(session["started_at"])
            elapsed = (datetime.utcnow() - started_at).seconds
            session["time_elapsed"] = elapsed
            session["time_remaining"] = max(0, session["time_limit"] - elapsed)
        
        # Get current question
        if session["status"] == SessionStatus.IN_PROGRESS:
            current_idx = session["current_question_index"]
            question_ids = session["question_ids"]
            
            if current_idx < len(question_ids):
                qid = question_ids[current_idx]
                session["current_question"] = await self._get_question_for_session(
                    qid,
                    session["questions"][qid]
                )
        
        return session
    
    async def submit_answer(self, session_id: str, user_id: str, answer_data: Dict) -> Dict:
        """Submit answer for a question"""
        
        # Get session
        session = firebase_client.get_data(f"practice_sessions/{user_id}/{session_id}")
        
        if not session:
            raise ValueError("Session not found")
        
        if session["status"] != SessionStatus.IN_PROGRESS:
            raise ValueError("Session is not in progress")
        
        # Verify question
        question_id = answer_data["question_id"]
        if question_id not in session["questions"]:
            raise ValueError("Question not in session")
        
        # Check if already answered
        if session["questions"][question_id]["status"] != "pending":
            raise ValueError("Question already answered")
        
        # Get question
        question = firebase_client.get_data(f"questions/{question_id}")
        if not question:
            raise ValueError("Question not found")
        
        # Check answer
        is_correct = await self._check_answer(question, answer_data["answer"])
        
        # Update question status
        session["questions"][question_id].update({
            "status": "answered",
            "answer": answer_data["answer"],
            "is_correct": is_correct,
            "time_taken": answer_data["time_taken_seconds"],
            "hints_used": answer_data.get("hints_used", 0)
        })
        
        # Update session stats
        session["questions_answered"] += 1
        if is_correct:
            session["correct_answers"] += 1
        else:
            session["incorrect_answers"] += 1
        
        if "time_per_question" not in session or session["time_per_question"] is None:
            session["time_per_question"] = []
        session["time_per_question"].append(answer_data["time_taken_seconds"])
        session["last_activity_at"] = datetime.utcnow().isoformat()
        
        # Move to next question
        current_idx = session["current_question_index"]
        question_ids = session["question_ids"]
        
        if current_idx + 1 < len(question_ids):
            session["current_question_index"] = current_idx + 1
            next_question_id = question_ids[current_idx + 1]
            next_question = await self._get_question_for_session(
                next_question_id,
                session["questions"][next_question_id]
            )
        else:
            # Session complete
            session["status"] = SessionStatus.COMPLETED
            session["completed_at"] = datetime.utcnow().isoformat()
            next_question = None
        
        # Save session
        firebase_client.set_data(f"practice_sessions/{user_id}/{session_id}", session)
        
        # Record attempt
        await self._record_attempt(user_id, question_id, answer_data, is_correct)
        
        return {
            "is_correct": is_correct,
            "correct_answer": self._get_correct_answer(question),
            "explanation": question.get("explanation"),
            "next_question": next_question,
            "session_completed": session["status"] == SessionStatus.COMPLETED,
            "progress": {
                "current": session["current_question_index"] + 1,
                "total": len(question_ids),
                "correct": session["correct_answers"],
                "incorrect": session["incorrect_answers"]
            }
        }
    
    async def _check_answer(self, question: Dict, answer: Any) -> bool:
        """Check if answer is correct"""
        
        correct_answers = question.get("correct_answers", [])
        
        # Handle different answer formats
        if isinstance(answer, str):
            return answer in correct_answers
        elif isinstance(answer, list):
            return set(answer) == set(correct_answers)
        elif isinstance(answer, dict):
            return answer.get("id") in correct_answers
        
        return False
    
    def _get_correct_answer(self, question: Dict) -> List[str]:
        """Get correct answer(s) for question"""
        
        return question.get("correct_answers", [])
    
    async def _record_attempt(self, user_id: str, question_id: str, answer_data: Dict, is_correct: bool):
        """Record question attempt"""
        
        attempt_id = str(uuid4())
        attempt = {
            "attempt_id": attempt_id,
            "user_id": user_id,
            "question_id": question_id,
            "answer": answer_data["answer"],
            "is_correct": is_correct,
            "time_taken_seconds": answer_data["time_taken_seconds"],
            "attempted_at": datetime.utcnow().isoformat()
        }
        
        firebase_client.set_data(f"attempts/{user_id}/{attempt_id}", attempt)
        
        # Update question stats
        question = firebase_client.get_data(f"questions/{question_id}")
        if question:
            times_used = question.get("times_used", 0) + 1
            times_correct = question.get("times_correct", 0) + (1 if is_correct else 0)
            
            firebase_client.update_data(f"questions/{question_id}", {
                "times_used": times_used,
                "times_correct": times_correct,
                "correct_rate": (times_correct / times_used * 100) if times_used > 0 else 0
            })
    
    async def skip_question(self, session_id: str, user_id: str) -> Dict:
        """Skip current question"""
        
        # Get session
        session = firebase_client.get_data(f"practice_sessions/{user_id}/{session_id}")
        
        if not session:
            raise ValueError("Session not found")
        
        if session["status"] != SessionStatus.IN_PROGRESS:
            raise ValueError("Session is not in progress")
        
        # Update question status
        current_idx = session["current_question_index"]
        question_ids = session["question_ids"]
        current_qid = question_ids[current_idx]
        
        session["questions"][current_qid]["status"] = "skipped"
        session["questions_skipped"] = session.get("questions_skipped", 0) + 1
        
        # Move to next question
        if current_idx + 1 < len(question_ids):
            session["current_question_index"] = current_idx + 1
            next_question_id = question_ids[current_idx + 1]
            next_question = await self._get_question_for_session(
                next_question_id,
                session["questions"][next_question_id]
            )
        else:
            # Session complete
            session["status"] = SessionStatus.COMPLETED
            session["completed_at"] = datetime.utcnow().isoformat()
            next_question = None
        
        session["last_activity_at"] = datetime.utcnow().isoformat()
        
        # Save session
        firebase_client.set_data(f"practice_sessions/{user_id}/{session_id}", session)
        
        return {
            "next_question": next_question,
            "session_completed": session["status"] == SessionStatus.COMPLETED,
            "progress": {
                "current": session["current_question_index"] + 1,
                "total": len(question_ids)
            }
        }
    
    async def pause_session(self, session_id: str, user_id: str):
        """Pause practice session"""
        
        session = firebase_client.get_data(f"practice_sessions/{user_id}/{session_id}")
        
        if not session:
            raise ValueError("Session not found")
        
        if session["status"] != SessionStatus.IN_PROGRESS:
            raise ValueError("Session is not in progress")
        
        session["status"] = SessionStatus.PAUSED
        session["last_activity_at"] = datetime.utcnow().isoformat()
        
        firebase_client.set_data(f"practice_sessions/{user_id}/{session_id}", session)
    
    async def resume_session(self, session_id: str, user_id: str) -> Dict:
        """Resume practice session"""
        
        session = firebase_client.get_data(f"practice_sessions/{user_id}/{session_id}")
        
        if not session:
            raise ValueError("Session not found")
        
        if session["status"] != SessionStatus.PAUSED:
            raise ValueError("Session is not paused")
        
        session["status"] = SessionStatus.IN_PROGRESS
        session["last_activity_at"] = datetime.utcnow().isoformat()
        
        # Get current question
        current_idx = session["current_question_index"]
        question_ids = session["question_ids"]
        
        if current_idx < len(question_ids):
            qid = question_ids[current_idx]
            session["current_question"] = await self._get_question_for_session(
                qid,
                session["questions"][qid]
            )
        
        firebase_client.set_data(f"practice_sessions/{user_id}/{session_id}", session)
        
        return session
    
    async def end_session(self, session_id: str, user_id: str) -> Dict:
        """End practice session and calculate results"""
        
        session = firebase_client.get_data(f"practice_sessions/{user_id}/{session_id}")
        
        if not session:
            raise ValueError("Session not found")
        
        # Calculate results
        results = await self._calculate_results(session, user_id)
        
        # Update session
        session["status"] = SessionStatus.COMPLETED
        session["completed_at"] = datetime.utcnow().isoformat()
        session["score"] = results["score"]
        session["accuracy"] = results["accuracy"]
        session["total_time_spent"] = results["total_time_spent"]
        
        firebase_client.set_data(f"practice_sessions/{user_id}/{session_id}", session)
        
        # Save results separately
        firebase_client.set_data(
            f"practice_results/{user_id}/{session_id}",
            results
        )
        
        return results
    
    async def _calculate_results(self, session: Dict, user_id: str) -> Dict:
        """Calculate session results"""
        
        total_questions = session["total_questions"]
        answered = session["questions_answered"]
        correct = session["correct_answers"]
        incorrect = session["incorrect_answers"]
        skipped = session.get("questions_skipped", 0)
        
        # Calculate scores
        accuracy = (correct / answered * 100) if answered > 0 else 0
        score = (correct / total_questions * 100)
        
        # Calculate time spent
        if session.get("completed_at"):
            started = datetime.fromisoformat(session["started_at"])
            completed = datetime.fromisoformat(session["completed_at"])
            total_time = (completed - started).seconds
        else:
            total_time = sum(session.get("time_per_question", []))
        
        return {
            "session_id": session["session_id"],
            "user_id": user_id,
            "type": session["type"],
            "score": round(score, 2),
            "accuracy": round(accuracy, 2),
            "total_time_spent": total_time,
            "correct_answers": correct,
            "incorrect_answers": incorrect,
            "skipped_questions": skipped,
            "total_questions": total_questions,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def get_session_results(self, session_id: str, user_id: str) -> Optional[Dict]:
        """Get results for a completed session"""
        
        results = firebase_client.get_data(f"practice_results/{user_id}/{session_id}")
        return results
    
    async def get_practice_history(
        self,
        user_id: str,
        days: int,
        practice_type: Optional[str]
    ) -> Dict:
        """Get user's practice history"""
        
        sessions = firebase_client.get_data(f"practice_sessions/{user_id}") or {}
        
        history = []
        total_time = 0
        total_score = 0
        total_accuracy = 0
        count = 0
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        for session_id, session in sessions.items():
            if session.get("created_at", "") < cutoff_date:
                continue
            
            if practice_type and session.get("type") != practice_type:
                continue
            
            if session.get("status") == SessionStatus.COMPLETED:
                history.append({
                    "session_id": session_id,
                    "type": session.get("type"),
                    "title": session.get("title"),
                    "subject": session.get("subject"),
                    "topic": session.get("topic"),
                    "company": session.get("company"),
                    "score": session.get("score"),
                    "accuracy": session.get("accuracy"),
                    "total_questions": session.get("total_questions"),
                    "correct_answers": session.get("correct_answers"),
                    "time_spent": session.get("total_time_spent", 0),
                    "completed_at": session.get("completed_at")
                })
                
                total_time += session.get("total_time_spent", 0)
                total_score += session.get("score", 0)
                total_accuracy += session.get("accuracy", 0)
                count += 1
        
        # Sort by date
        history.sort(key=lambda x: x["completed_at"], reverse=True)
        
        return {
            "total_sessions": count,
            "total_time_spent": total_time // 60,
            "average_score": round(total_score / count, 2) if count > 0 else 0,
            "average_accuracy": round(total_accuracy / count, 2) if count > 0 else 0,
            "recent_sessions": history[:10]
        }
    
    async def get_practice_stats(self, user_id: str) -> Dict:
        """Get practice statistics"""
        
        sessions = firebase_client.get_data(f"practice_sessions/{user_id}") or {}
        
        stats = {
            "total_sessions": 0,
            "completed_sessions": 0,
            "total_questions_attempted": 0,
            "total_correct": 0,
            "by_type": {},
            "by_subject": {},
            "daily_activity": {}
        }
        
        for session_id, session in sessions.items():
            stats["total_sessions"] += 1
            
            if session.get("status") == SessionStatus.COMPLETED:
                stats["completed_sessions"] += 1
                stats["total_questions_attempted"] += session.get("questions_answered", 0)
                stats["total_correct"] += session.get("correct_answers", 0)
                
                # By type
                s_type = session.get("type")
                if s_type not in stats["by_type"]:
                    stats["by_type"][s_type] = {
                        "count": 0,
                        "total_questions": 0,
                        "correct": 0
                    }
                stats["by_type"][s_type]["count"] += 1
                stats["by_type"][s_type]["total_questions"] += session.get("questions_answered", 0)
                stats["by_type"][s_type]["correct"] += session.get("correct_answers", 0)
                
                # By subject
                subject = session.get("subject")
                if subject:
                    if subject not in stats["by_subject"]:
                        stats["by_subject"][subject] = {
                            "count": 0,
                            "total_questions": 0,
                            "correct": 0
                        }
                    stats["by_subject"][subject]["count"] += 1
                    stats["by_subject"][subject]["total_questions"] += session.get("questions_answered", 0)
                    stats["by_subject"][subject]["correct"] += session.get("correct_answers", 0)
        
        # Calculate accuracy
        if stats["total_questions_attempted"] > 0:
            stats["overall_accuracy"] = round(
                stats["total_correct"] / stats["total_questions_attempted"] * 100, 2
            )
        
        return stats
    
    async def get_available_topics(self, subject: str) -> List[str]:
        """Get available topics for a subject"""
        
        topics_ref = firebase_client.get_reference(f"topics/{subject}")
        topics = topics_ref.get() or []
        return topics
    
    async def _get_random_questions(
        self,
        total: int,
        subjects: Optional[List[str]] = None,
        difficulties: Optional[List[str]] = None
    ) -> List[Dict]:
        """Get random questions"""
        
        all_questions = firebase_client.get_data("questions") or {}
        
        filtered = []
        for qid, question in all_questions.items():
            if question.get("status") != "approved":
                continue
            
            if subjects and question.get("subject") not in subjects:
                continue
            
            if difficulties and question.get("difficulty") not in difficulties:
                continue
            
            filtered.append({
                "question_id": qid,
                **question
            })
        
        # Shuffle and return requested number
        random.shuffle(filtered)
        return filtered[:total]
    
    async def _get_mock_test_questions(self, config: Dict) -> List[Dict]:
        """Get questions for mock test"""
        
        all_questions = firebase_client.get_data("questions") or {}
        
        # Filter by subject and status
        subject_questions = []
        for qid, question in all_questions.items():
            if (question.get("status") == "approved" and
                question.get("subject") == config["subject"]):
                subject_questions.append({
                    "question_id": qid,
                    **question
                })
        
        # Apply difficulty distribution if specified
        if config.get("difficulty_distribution"):
            distribution = config["difficulty_distribution"]
            selected = []
            
            for difficulty, count in distribution.items():
                difficulty_questions = [
                    q for q in subject_questions
                    if q.get("difficulty") == difficulty
                ]
                random.shuffle(difficulty_questions)
                selected.extend(difficulty_questions[:count])
            
            return selected
        
        # Otherwise random selection
        random.shuffle(subject_questions)
        return subject_questions[:config.get("total_questions", 30)]
    
    async def _get_company_questions(
        self,
        company: str,
        role: Optional[str],
        total: int,
        difficulty_focus: Optional[str]
    ) -> List[Dict]:
        """Get company-specific questions"""
        
        all_questions = firebase_client.get_data("questions") or {}
        
        filtered = []
        for qid, question in all_questions.items():
            if question.get("status") != "approved":
                continue
            
            companies = question.get("companies", [])
            if company not in companies:
                continue
            
            if role and role not in question.get("roles", []):
                continue
            
            if difficulty_focus and question.get("difficulty") != difficulty_focus:
                continue
            
            filtered.append({
                "question_id": qid,
                **question
            })
        
        random.shuffle(filtered)
        return filtered[:total]
    
    async def create_company_grid(
        self,
        company: str,
        question_ids: List[str],
        created_by: str
    ) -> Dict:
        """Create a company-specific question grid (admin)"""
        
        # Validate questions
        valid_questions = []
        difficulties = {"easy": 0, "medium": 0, "hard": 0, "expert": 0}
        topics = set()
        
        for qid in question_ids:
            question = firebase_client.get_data(f"questions/{qid}")
            if question and question.get("status") == "approved":
                valid_questions.append(qid)
                difficulties[question.get("difficulty", "medium")] += 1
                topics.add(question.get("topic"))
        
        grid = {
            "company": company,
            "question_ids": valid_questions,
            "total_questions": len(valid_questions),
            "difficulty_breakdown": difficulties,
            "topics": list(topics),
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat(),
            "average_score": 0
        }
        
        # Save grid
        firebase_client.set_data(f"company_grids/{company}", grid)
        
        return grid
