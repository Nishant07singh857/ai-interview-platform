"""
Gemini Service - AI question generation using Google Gemini
"""

import os
import json
import logging
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import settings
import time
from uuid import uuid4

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for generating questions using Google Gemini"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
        self.initialized = False
        
        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY not found in settings")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.initialized = True
            logger.info(f"✅ Gemini service initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {str(e)}")
    
    async def generate_questions_for_topic(
        self,
        subject: str,
        topic: str,
        count: int = 5,
        difficulty: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate multiple choice questions for a topic using Gemini"""
        
        if not self.initialized:
            logger.error("❌ Gemini service not initialized")
            return self._get_fallback_questions(topic, count)
        
        prompt = f"""Generate {count} multiple choice questions about {topic} in {subject}.
        
        Difficulty level: {difficulty or 'mixed'} (mix of easy, medium, and hard)
        
        For EACH question, provide:
        1. A clear question title
        2. Four options labeled A, B, C, D
        3. The correct answer (A, B, C, or D)
        4. A detailed explanation
        5. Difficulty level (easy, medium, or hard)
        6. 2-3 relevant tags
        
        Return ONLY a valid JSON array with this exact structure:
        [
            {{
                "title": "What is the main purpose of linear regression?",
                "description": "Basic concept question",
                "options": [
                    {{"id": "A", "text": "Classification of data", "is_correct": false}},
                    {{"id": "B", "text": "Predicting continuous values", "is_correct": true}},
                    {{"id": "C", "text": "Clustering similar items", "is_correct": false}},
                    {{"id": "D", "text": "Reducing dimensionality", "is_correct": false}}
                ],
                "explanation": "Linear regression is used to predict a continuous target variable based on one or more input features.",
                "difficulty": "easy",
                "tags": ["linear_regression", "supervised_learning", "regression"]
            }}
        ]
        
        Ensure questions are accurate, educational, and appropriate for interview preparation.
        Only one option should be correct per question.
        """
        
        try:
            logger.info(f"🎯 Generating {count} questions for {subject} - {topic}")
            
            # Generate content with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await self.model.generate_content_async(prompt)
                    questions = self._parse_questions(response.text)
                    
                    if questions and len(questions) > 0:
                        logger.info(f"✅ Generated {len(questions)} questions")
                        return questions
                    else:
                        logger.warning(f"⚠️ Attempt {attempt + 1}: No questions parsed, retrying...")
                        time.sleep(1)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2)
            
            return self._get_fallback_questions(topic, count)
            
        except Exception as e:
            logger.error(f"❌ Error generating questions: {str(e)}")
            return self._get_fallback_questions(topic, count)
    
    def _parse_questions(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse JSON response from Gemini"""
        
        try:
            # Clean the response text
            text = response_text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            # Try to find JSON array
            start_idx = text.find('[')
            end_idx = text.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                questions = json.loads(json_str)
                
                # Validate and clean each question
                validated = []
                for q in questions:
                    if self._validate_question(q):
                        # Ensure options are in correct format
                        if "options" in q and isinstance(q["options"], list):
                            # If options are strings, convert to dict format
                            if q["options"] and isinstance(q["options"][0], str):
                                formatted_options = []
                                for idx, opt_text in enumerate(q["options"]):
                                    opt_id = chr(65 + idx)  # A, B, C, D
                                    is_correct = (opt_id == q.get("correct_answer", "A"))
                                    formatted_options.append({
                                        "id": opt_id,
                                        "text": opt_text,
                                        "is_correct": is_correct
                                    })
                                q["options"] = formatted_options
                        validated.append(q)
                
                return validated
            
            return []
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"❌ Parse error: {str(e)}")
            return []
    
    def _validate_question(self, question: Dict) -> bool:
        """Validate question has required fields"""
        
        required_fields = ["title", "options", "explanation", "difficulty"]
        
        for field in required_fields:
            if field not in question:
                logger.warning(f"⚠️ Question missing required field: {field}")
                return False
        
        # Check options
        if not isinstance(question["options"], list) or len(question["options"]) != 4:
            logger.warning("⚠️ Question must have exactly 4 options")
            return False
        
        return True
    
    def _get_fallback_questions(self, topic: str, count: int) -> List[Dict[str, Any]]:
        """Generate fallback questions if API fails"""
        
        fallback = []
        for i in range(min(count, 5)):  # Max 5 fallback questions
            fallback.append({
                "title": f"What is {topic}?",
                "description": f"Basic concept question about {topic}",
                "options": [
                    {"id": "A", "text": f"A fundamental concept in {topic}", "is_correct": True},
                    {"id": "B", "text": "An unrelated concept", "is_correct": False},
                    {"id": "C", "text": "A programming language", "is_correct": False},
                    {"id": "D", "text": "A database system", "is_correct": False}
                ],
                "explanation": f"{topic} is a fundamental concept in this field. It involves understanding core principles and applications in real-world scenarios.",
                "difficulty": "medium",
                "tags": [topic.lower().replace(" ", "_"), "basics", "fundamental"]
            })
        return fallback
    
    async def generate_explanation(self, question: str, answer: str) -> str:
        """Generate detailed explanation for an answer"""
        
        if not self.initialized:
            return "Explanation not available"
        
        prompt = f"""Provide a detailed explanation for this question and answer:
        
        Question: {question}
        Correct Answer: {answer}
        
        Explain why this answer is correct and provide additional context.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"❌ Error generating explanation: {str(e)}")
            return "Explanation not available"

# Global instance
gemini_service = GeminiService()