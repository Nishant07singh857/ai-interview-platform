"""
Question Service - Complete question management business logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from uuid import uuid4

from app.core.database import firebase_client
from app.core.cache import cache_manager
from app.models.question import Question, DifficultyLevel
from app.schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    QuestionDetailResponse, QuestionWithAnswerResponse,
    QuestionAttemptCreate, QuestionAttemptResponse
)

logger = logging.getLogger(__name__)

class QuestionService:
    """Question service with complete business logic"""

    def _normalize_question_data(self, question_id: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize question data to satisfy response schemas"""

        data = (question or {}).copy()

        data["question_id"] = data.get("question_id") or data.get("id") or question_id

        subject = data.get("subject") or data.get("subject_area")
        if subject:
            subject_value = str(subject).lower()
            subject_map = {
                "ai": "artificial_intelligence",
                "artificial-intelligence": "artificial_intelligence",
                "ml": "machine_learning",
                "machine-learning": "machine_learning",
                "dl": "deep_learning",
                "deep-learning": "deep_learning",
                "ds": "data_science",
                "data-science": "data_science",
                "da": "data_analysis",
                "data-analysis": "data_analysis",
            }
            subject_value = subject_map.get(subject_value, subject_value)
        else:
            subject_value = None
        allowed_subjects = {
            "machine_learning",
            "deep_learning",
            "data_science",
            "data_analysis",
            "artificial_intelligence",
        }
        data["subject"] = subject_value if subject_value in allowed_subjects else "data_science"

        data["topic"] = data.get("topic") or "general"
        data.setdefault("subtopic", None)

        qtype = data.get("type") or data.get("question_type")
        if qtype:
            qtype_value = str(qtype).lower().replace(" ", "_").replace("-", "_")
            qtype_map = {
                "multiple_choice": "mcq",
                "multiplechoice": "mcq",
                "multi_select": "multiple_select",
                "multi-select": "multiple_select",
                "truefalse": "true_false",
                "fillblank": "fill_blank",
                "systemdesign": "system_design",
                "case-study": "case_study",
                "case study": "case_study",
            }
            qtype_value = qtype_map.get(qtype_value, qtype_value)
        else:
            qtype_value = None
        allowed_types = {
            "mcq",
            "code",
            "theory",
            "system_design",
            "case_study",
            "multiple_select",
            "true_false",
            "fill_blank",
            "matching",
        }
        data["type"] = qtype_value if qtype_value in allowed_types else "mcq"

        difficulty = data.get("difficulty") or data.get("level")
        if difficulty:
            diff_value = str(difficulty).lower()
            diff_map = {
                "beginner": "easy",
                "intermediate": "medium",
                "advanced": "hard",
            }
            diff_value = diff_map.get(diff_value, diff_value)
        else:
            diff_value = None
        allowed_difficulties = {"easy", "medium", "hard", "expert"}
        data["difficulty"] = diff_value if diff_value in allowed_difficulties else "medium"

        status = data.get("status")
        if status:
            status_value = str(status).lower()
        else:
            status_value = None
        allowed_status = {"draft", "review", "approved", "rejected", "archived"}
        data["status"] = status_value if status_value in allowed_status else "approved"

        data["title"] = data.get("title") or ""
        data["description"] = data.get("description") or ""
        data.setdefault("instructions", None)

        data.setdefault("options", None)
        data.setdefault("code_snippet", None)
        data.setdefault("programming_language", None)
        data.setdefault("time_limit", None)
        data.setdefault("memory_limit", None)
        data.setdefault("word_limit", None)
        data.setdefault("requirements", None)
        data.setdefault("constraints", None)
        if data.get("diagrams_required") is None:
            data["diagrams_required"] = False
        data.setdefault("case_data", None)
        data.setdefault("datasets", None)

        data["explanation"] = data.get("explanation") or ""
        data.setdefault("detailed_explanation", None)
        hints = data.get("hints") or []
        data["hints"] = hints
        data["all_hints"] = data.get("all_hints") or hints
        data.setdefault("common_mistakes", None)

        data["references"] = data.get("references") or []
        data["videos"] = data.get("videos") or []
        data["images"] = data.get("images") or []

        data["tags"] = data.get("tags") or []
        data["companies"] = data.get("companies") or []
        data["roles"] = data.get("roles") or []

        data["times_used"] = data.get("times_used") or 0
        data["correct_rate"] = data.get("correct_rate") or 0.0
        data["avg_time_seconds"] = data.get("avg_time_seconds") or 0

        if not data.get("created_at"):
            data["created_at"] = datetime.utcnow().isoformat()

        return data
    
    async def get_questions(
        self,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[DifficultyLevel] = None,
        type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[QuestionResponse]:
        """Get questions with filters"""
        
        # Try cache first
        cache_key = f"questions:{subject}:{topic}:{difficulty}:{type}:{offset}:{limit}"
        cached = await cache_manager.get(cache_key)
        if cached:
            try:
                return [QuestionResponse(**self._normalize_question_data(q.get("question_id", ""), q)) for q in cached]
            except Exception as e:
                logger.warning(f"Invalid cached questions for {cache_key}: {str(e)}. Refreshing cache.")
                await cache_manager.delete(cache_key)
        
        # Get all questions
        questions_data = firebase_client.get_data("questions") or {}
        
        # Apply filters
        filtered = []
        for question_id, question in questions_data.items():
            if question.get("status") != "approved":
                continue
                
            if subject and question.get("subject") != subject:
                continue
            if topic and question.get("topic") != topic:
                continue
            if difficulty and question.get("difficulty") != difficulty:
                continue
            if type and question.get("type") != type:
                continue
            
            # Normalize and remove answer fields for public view
            question_copy = self._normalize_question_data(question_id, question)
            if "correct_answers" in question_copy:
                del question_copy["correct_answers"]
            if "options" in question_copy:
                # Remove is_correct from options
                for opt in question_copy.get("options", []):
                    if "is_correct" in opt:
                        del opt["is_correct"]
            
            filtered.append(QuestionResponse(**question_copy))
        
        # Sort by created_at
        filtered.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        result = filtered[offset:offset + limit]
        
        # Cache for 1 hour
        await cache_manager.set(
            cache_key,
            [q.dict() for q in result],
            ttl=3600
        )
        
        return result
    
    async def search_questions(self, query: str, limit: int) -> List[QuestionResponse]:
        """Search questions by text"""
        
        questions_data = firebase_client.get_data("questions") or {}
        
        results = []
        query = query.lower()
        
        for question_id, question in questions_data.items():
            if question.get("status") != "approved":
                continue
                
            # Search in title and description
            if (query in question.get("title", "").lower() or
                query in question.get("description", "").lower() or
                query in question.get("explanation", "").lower()):
                
                # Remove answer fields
                question_copy = question.copy()
                if "correct_answers" in question_copy:
                    del question_copy["correct_answers"]
                if "options" in question_copy:
                    for opt in question_copy.get("options", []):
                        if "is_correct" in opt:
                            del opt["is_correct"]
                
                results.append(QuestionResponse(**question_copy))
            
            if len(results) >= limit:
                break
        
        return results
    
    async def get_question(self, question_id: str) -> Optional[QuestionDetailResponse]:
        """Get question by ID (without answers)"""
        
        # Try cache first
        cache_key = f"question:{question_id}"
        cached = await cache_manager.get(cache_key)
        if cached:
            try:
                normalized_cached = self._normalize_question_data(question_id, cached)
                return QuestionDetailResponse(**normalized_cached)
            except Exception as e:
                logger.warning(f"Invalid cached question {question_id}: {str(e)}. Refreshing cache.")
                await cache_manager.delete(cache_key)
        
        question = firebase_client.get_data(f"questions/{question_id}")
        
        if not question or question.get("status") != "approved":
            return None
        
        # Remove answers
        question_copy = self._normalize_question_data(question_id, question)
        if "correct_answers" in question_copy:
            del question_copy["correct_answers"]
        if "options" in question_copy:
            for opt in question_copy.get("options", []):
                if "is_correct" in opt:
                    del opt["is_correct"]
        if "all_hints" not in question_copy:
            question_copy["all_hints"] = question_copy.get("hints", [])
        
        result = QuestionDetailResponse(**question_copy)
        
        # Cache for 1 hour
        await cache_manager.set(cache_key, result.dict(), ttl=3600)
        
        return result
    
    async def get_question_with_answers(self, question_id: str) -> Optional[QuestionWithAnswerResponse]:
        """Get question with answers (pro feature)"""
        
        question = firebase_client.get_data(f"questions/{question_id}")
        
        if not question or question.get("status") != "approved":
            return None
        
        question_copy = self._normalize_question_data(question_id, question)
        return QuestionWithAnswerResponse(**question_copy)
    
    async def attempt_question(
        self,
        user_id: str,
        question_id: str,
        attempt: QuestionAttemptCreate
    ) -> QuestionAttemptResponse:
        """Process question attempt"""
        
        # Get question
        question = firebase_client.get_data(f"questions/{question_id}")
        
        if not question:
            raise ValueError("Question not found")
        
        # Check answer based on question type
        is_correct = await self._check_answer(question, attempt.answer)
        
        # Create attempt record
        attempt_id = str(uuid4())
        attempt_data = {
            "attempt_id": attempt_id,
            "user_id": user_id,
            "question_id": question_id,
            "answer": attempt.answer,
            "is_correct": is_correct,
            "time_taken_seconds": attempt.time_taken_seconds,
            "hints_used": attempt.hints_used,
            "attempted_at": datetime.utcnow().isoformat()
        }
        
        # Save attempt
        firebase_client.set_data(
            f"attempts/{user_id}/{attempt_id}",
            attempt_data
        )
        
        # Update question stats
        await self._update_question_stats(question_id, is_correct, attempt.time_taken_seconds)
        
        # Update user progress
        await self._update_user_progress(user_id, question, is_correct)
        
        # Prepare response
        correct_answer = await self._get_correct_answer(question)
        
        return QuestionAttemptResponse(
            attempt_id=attempt_id,
            question_id=question_id,
            is_correct=is_correct,
            time_taken_seconds=attempt.time_taken_seconds,
            hints_used=attempt.hints_used,
            explanation=question.get("explanation", ""),
            correct_answer=correct_answer,
            attempted_at=datetime.utcnow()
        )
    
    async def _check_answer(self, question: Dict, answer: Any) -> bool:
        """Check if answer is correct based on question type"""
        
        question_type = question.get("type")
        
        if question_type == "mcq":
            # Answer should be option ID
            correct_options = [
                opt["id"] for opt in question.get("options", [])
                if opt.get("is_correct", False)
            ]
            return answer in correct_options
            
        elif question_type == "multiple_select":
            # Answer should be list of option IDs
            correct_options = [
                opt["id"] for opt in question.get("options", [])
                if opt.get("is_correct", False)
            ]
            return set(answer) == set(correct_options)
            
        elif question_type == "true_false":
            # Answer should be boolean
            return answer == question.get("correct_answer")
            
        elif question_type == "code":
            # Run test cases
            return await self._run_code_tests(answer, question.get("test_cases", []))
            
        elif question_type == "theory":
            # Check key points
            return await self._check_theory_answer(answer, question.get("key_points", []))
            
        elif question_type == "fill_blank":
            # Check exact match or case-insensitive
            correct = question.get("correct_answer", "")
            return answer.strip().lower() == correct.strip().lower()
            
        elif question_type == "matching":
            # Check matching pairs
            correct_pairs = question.get("correct_pairs", {})
            return answer == correct_pairs
        
        return False
    
    async def _run_code_tests(self, code: str, test_cases: List[Dict]) -> bool:
        """Run code against test cases"""
        # This would integrate with a code execution service
        # For now, return True for demonstration
        return True
    
    async def _check_theory_answer(self, answer: str, key_points: List[str]) -> bool:
        """Check theory answer against key points"""
        # This would use NLP to check if key points are covered
        # For now, return True for demonstration
        return True
    
    async def _get_correct_answer(self, question: Dict) -> Any:
        """Get correct answer for response"""
        
        question_type = question.get("type")
        
        if question_type == "mcq":
            correct_options = [
                opt for opt in question.get("options", [])
                if opt.get("is_correct", False)
            ]
            return correct_options[0] if correct_options else None
            
        elif question_type == "multiple_select":
            return [
                opt for opt in question.get("options", [])
                if opt.get("is_correct", False)
            ]
            
        elif question_type in ["true_false", "fill_blank"]:
            return question.get("correct_answer")
            
        elif question_type == "matching":
            return question.get("correct_pairs")
            
        elif question_type == "theory":
            return {
                "expected_answer": question.get("expected_answer"),
                "key_points": question.get("key_points")
            }
        
        return None
    
    async def _update_question_stats(
        self,
        question_id: str,
        is_correct: bool,
        time_taken: int
    ):
        """Update question statistics"""
        
        question = firebase_client.get_data(f"questions/{question_id}")
        
        if question:
            times_used = question.get("times_used", 0) + 1
            times_correct = question.get("times_correct", 0) + (1 if is_correct else 0)
            correct_rate = (times_correct / times_used) * 100
            
            # Update average time
            avg_time = question.get("avg_time_seconds", 0)
            new_avg_time = (avg_time * (times_used - 1) + time_taken) / times_used
            
            firebase_client.update_data(f"questions/{question_id}", {
                "times_used": times_used,
                "times_correct": times_correct,
                "correct_rate": round(correct_rate, 2),
                "avg_time_seconds": round(new_avg_time)
            })
    
    async def _update_user_progress(self, user_id: str, question: Dict, is_correct: bool):
        """Update user progress"""
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Get today's progress
        progress_path = f"progress/{user_id}/{today}"
        progress = firebase_client.get_data(progress_path) or {
            "questions_attempted": 0,
            "correct_answers": 0,
            "subjects_practiced": [],
            "topics_practiced": []
        }
        
        # Update counts
        progress["questions_attempted"] += 1
        if is_correct:
            progress["correct_answers"] += 1
        
        # Add subject and topic
        subject = question.get("subject")
        if subject and subject not in progress["subjects_practiced"]:
            progress["subjects_practiced"].append(subject)
        
        topic = question.get("topic")
        if topic and topic not in progress["topics_practiced"]:
            progress["topics_practiced"].append(topic)
        
        # Calculate accuracy
        progress["accuracy"] = round(
            progress["correct_answers"] / progress["questions_attempted"] * 100, 2
        )
        
        # Save progress
        firebase_client.set_data(progress_path, progress)
        
        # Update user stats
        user_stats = firebase_client.get_data(f"users/{user_id}/stats") or {
            "total_questions": 0,
            "correct_answers": 0
        }
        
        user_stats["total_questions"] += 1
        if is_correct:
            user_stats["correct_answers"] += 1
        
        user_stats["accuracy"] = round(
            user_stats["correct_answers"] / user_stats["total_questions"] * 100, 2
        )
        
        firebase_client.update_data(f"users/{user_id}", {
            "stats": user_stats
        })
    
    async def get_hint(self, question_id: str, hint_number: int) -> Optional[str]:
        """Get hint for question"""
        
        question = firebase_client.get_data(f"questions/{question_id}")
        
        if not question:
            return None
        
        hints = question.get("hints", [])
        
        if hint_number <= len(hints):
            return hints[hint_number - 1]
        
        return None
    
    async def get_topics(self, subject: Optional[str] = None) -> List[Dict]:
        """Get all topics"""
        
        topics_data = firebase_client.get_data("topics") or {}
        
        topics = []
        for topic_id, topic in topics_data.items():
            if subject and topic.get("subject") != subject:
                continue
            topics.append({
                "topic_id": topic_id,
                **topic
            })
        
        return topics
    
    async def get_topic(self, topic_id: str) -> Optional[Dict]:
        """Get topic by ID"""
        
        return firebase_client.get_data(f"topics/{topic_id}")
    
    async def get_public_sets(self, type: Optional[str], limit: int) -> List[Dict]:
        """Get public question sets"""
        
        sets_data = firebase_client.get_data("question_sets") or {}
        
        result = []
        for set_id, set_data in sets_data.items():
            if set_data.get("is_public", False):
                if type and set_data.get("type") != type:
                    continue
                result.append({
                    "set_id": set_id,
                    **set_data
                })
            
            if len(result) >= limit:
                break
        
        return result
    
    async def get_question_set(self, set_id: str) -> Optional[Dict]:
        """Get question set by ID"""
        
        set_data = firebase_client.get_data(f"question_sets/{set_id}")
        
        if not set_data:
            return None
        
        # Get questions in set
        question_ids = set_data.get("questions", [])
        questions = []
        
        for qid in question_ids:
            question = await self.get_question(qid)
            if question:
                questions.append(question)
        
        set_data["questions"] = questions
        
        return set_data
    
    async def create_question(
        self,
        question_data: QuestionCreate,
        created_by: str
    ) -> QuestionResponse:
        """Create a new question (admin)"""
        
        question_id = str(uuid4())
        
        question_dict = question_data.dict()
        question_dict.update({
            "question_id": question_id,
            "status": "approved",
            "times_used": 0,
            "times_correct": 0,
            "correct_rate": 0.0,
            "avg_time_seconds": 0,
            "difficulty_rating": 0.0,
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat(),
            "version": 1
        })
        
        # Save to database
        firebase_client.set_data(f"questions/{question_id}", question_dict)
        
        # Remove answer fields for response
        response_dict = question_dict.copy()
        if "correct_answers" in response_dict:
            del response_dict["correct_answers"]
        if "options" in response_dict:
            for opt in response_dict.get("options", []):
                if "is_correct" in opt:
                    del opt["is_correct"]
        
        return QuestionResponse(**response_dict)
    
    async def update_question(
        self,
        question_id: str,
        update_data: Dict[str, Any],
        updated_by: str
    ) -> Optional[QuestionResponse]:
        """Update a question (admin)"""
        
        # Check if question exists
        question = firebase_client.get_data(f"questions/{question_id}")
        
        if not question:
            return None
        
        # Add update metadata
        update_data["updated_by"] = updated_by
        update_data["updated_at"] = datetime.utcnow().isoformat()
        update_data["version"] = question.get("version", 1) + 1
        
        # Save previous version
        firebase_client.set_data(
            f"questions_versions/{question_id}/{question.get('version', 1)}",
            question
        )
        
        # Update question
        firebase_client.update_data(f"questions/{question_id}", update_data)
        
        # Get updated question
        updated = firebase_client.get_data(f"questions/{question_id}")
        
        # Remove answer fields for response
        if "correct_answers" in updated:
            del updated["correct_answers"]
        if "options" in updated:
            for opt in updated.get("options", []):
                if "is_correct" in opt:
                    del opt["is_correct"]
        
        # Clear cache
        await cache_manager.delete(f"question:{question_id}")
        
        return QuestionResponse(**updated)
    
    async def delete_question(self, question_id: str) -> bool:
        """Delete a question (admin)"""
        
        # Check if question exists
        question = firebase_client.get_data(f"questions/{question_id}")
        
        if not question:
            return False
        
        # Archive instead of delete
        firebase_client.update_data(f"questions/{question_id}", {
            "status": "archived",
            "archived_at": datetime.utcnow().isoformat()
        })
        
        # Clear cache
        await cache_manager.delete(f"question:{question_id}")
        
        return True
    
    async def bulk_create_questions(
        self,
        questions: List[QuestionCreate],
        created_by: str
    ) -> List[QuestionResponse]:
        """Bulk create questions (admin)"""
        
        results = []
        
        for question_data in questions:
            try:
                result = await self.create_question(question_data, created_by)
                results.append(result)
            except Exception as e:
                logger.error(f"Error creating question in bulk: {str(e)}")
        
        return results
    
    async def create_question_set(
        self,
        name: str,
        description: Optional[str],
        question_ids: List[str],
        created_by: str
    ) -> Dict:
        """Create a question set (admin)"""
        
        set_id = str(uuid4())
        
        # Validate questions exist
        valid_questions = []
        for qid in question_ids:
            if firebase_client.get_data(f"questions/{qid}"):
                valid_questions.append(qid)
        
        set_data = {
            "set_id": set_id,
            "name": name,
            "description": description,
            "questions": valid_questions,
            "total_questions": len(valid_questions),
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat(),
            "is_public": True
        }
        
        # Save set
        firebase_client.set_data(f"question_sets/{set_id}", set_data)
        
        return set_data
    
    async def add_questions_to_set(self, set_id: str, question_ids: List[str]):
        """Add questions to set (admin)"""
        
        set_data = firebase_client.get_data(f"question_sets/{set_id}")
        
        if not set_data:
            raise ValueError("Question set not found")
        
        current_questions = set(set_data.get("questions", []))
        new_questions = set(question_ids)
        
        # Merge and validate
        all_questions = list(current_questions | new_questions)
        
        firebase_client.update_data(f"question_sets/{set_id}", {
            "questions": all_questions,
            "total_questions": len(all_questions),
            "updated_at": datetime.utcnow().isoformat()
        })
    
    async def remove_questions_from_set(self, set_id: str, question_ids: List[str]):
        """Remove questions from set (admin)"""
        
        set_data = firebase_client.get_data(f"question_sets/{set_id}")
        
        if not set_data:
            raise ValueError("Question set not found")
        
        current_questions = set(set_data.get("questions", []))
        remove_set = set(question_ids)
        
        remaining = list(current_questions - remove_set)
        
        firebase_client.update_data(f"question_sets/{set_id}", {
            "questions": remaining,
            "total_questions": len(remaining),
            "updated_at": datetime.utcnow().isoformat()
        })
