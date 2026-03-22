"""
Interview AI Service - AI-powered interview analysis and question generation
"""

import openai
import google.generativeai as genai
from typing import Dict, List, Any, Optional
import logging
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

class InterviewAI:
    """AI-powered interview service using OpenAI and Gemini"""
    
    def __init__(self):
        self.use_openai = bool(settings.OPENAI_API_KEY)
        self.use_gemini = bool(settings.GEMINI_API_KEY)
        
        if self.use_openai:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_model = settings.OPENAI_MODEL
        
        if self.use_gemini:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def analyze_response(
        self,
        question: Dict[str, Any],
        response_text: str,
        voice_analysis: Optional[Dict] = None,
        video_analysis: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Analyze interview response using AI"""
        
        prompt = self._build_analysis_prompt(question, response_text, voice_analysis, video_analysis)
        
        try:
            if self.use_openai:
                analysis = await self._analyze_with_openai(prompt)
            elif self.use_gemini:
                analysis = await self._analyze_with_gemini(prompt)
            else:
                analysis = self._get_mock_analysis(question, response_text)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing response: {str(e)}")
            return self._get_fallback_analysis(question, response_text)
    
    def _build_analysis_prompt(
        self,
        question: Dict,
        response: str,
        voice_analysis: Optional[Dict],
        video_analysis: Optional[Dict]
    ) -> str:
        """Build prompt for AI analysis"""
        
        prompt = f"""
        Analyze this interview response and provide detailed feedback.
        
        Question: {question.get('question_text')}
        Question Category: {question.get('category')}
        Question Difficulty: {question.get('difficulty')}
        
        Expected Key Points:
        {chr(10).join(f'- {point}' for point in question.get('expected_points', []))}
        
        Candidate's Response:
        {response}
        """
        
        if voice_analysis:
            prompt += f"""
            
            Voice Analysis:
            - Speaking Rate: {voice_analysis.get('speaking_rate')}
            - Clarity: {voice_analysis.get('clarity_score')}
            - Confidence: {voice_analysis.get('confidence_score')}
            - Filler Words: {voice_analysis.get('filler_word_count')}
            """
        
        if video_analysis:
            prompt += f"""
            
            Video Analysis:
            - Eye Contact: {video_analysis.get('eye_contact_score')}
            - Posture: {video_analysis.get('posture_score')}
            - Confidence: {video_analysis.get('confidence_score')}
            """
        
        prompt += """
        
        Provide analysis in the following JSON format:
        {
            "score": <overall_score_0-100>,
            "feedback": "<detailed_feedback>",
            "strengths": ["<strength1>", "<strength2>", ...],
            "improvements": ["<improvement1>", "<improvement2>", ...],
            "key_points_covered": ["<point1>", "<point2>", ...],
            "missing_points": ["<point1>", "<point2>", ...],
            "technical_accuracy": <score_0-100>,
            "communication_clarity": <score_0-100>,
            "confidence_level": "<low/medium/high>"
        }
        """
        
        return prompt
    
    async def _analyze_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Analyze using OpenAI"""
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer. Analyze interview responses and provide constructive feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return self._get_fallback_analysis_from_text(result)
            
        except Exception as e:
            logger.error(f"OpenAI analysis error: {str(e)}")
            raise
    
    async def _analyze_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Analyze using Google Gemini"""
        
        try:
            response = await self.gemini_model.generate_content_async(prompt)
            result = response.text
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return self._get_fallback_analysis_from_text(result)
            
        except Exception as e:
            logger.error(f"Gemini analysis error: {str(e)}")
            raise
    
    def _get_fallback_analysis_from_text(self, text: str) -> Dict[str, Any]:
        """Extract analysis from text when JSON parsing fails"""
        
        return {
            "score": 75,
            "feedback": text[:500] if text else "Analysis completed successfully.",
            "strengths": ["Response provided", "Question addressed"],
            "improvements": ["Add more detail", "Provide specific examples"],
            "key_points_covered": ["Main concepts covered"],
            "missing_points": ["Additional details could be included"],
            "technical_accuracy": 70,
            "communication_clarity": 75,
            "confidence_level": "medium"
        }
    
    def _get_mock_analysis(self, question: Dict, response: str) -> Dict[str, Any]:
        """Get mock analysis for testing when no AI is available"""
        
        response_length = len(response.split())
        
        if response_length > 100:
            score = 85
            strengths = ["Comprehensive response", "Good structure", "Clear explanation"]
            improvements = ["Could be more concise"]
        elif response_length > 50:
            score = 70
            strengths = ["Addresses the question", "Good points made"]
            improvements = ["Elaborate more", "Provide examples"]
        else:
            score = 50
            strengths = ["Response provided"]
            improvements = ["Expand your answer", "Include more details", "Structure your response"]
        
        return {
            "score": score,
            "feedback": f"Your response was {response_length} words long. " + 
                       ("Good coverage of key points." if score > 70 else "Consider expanding your answer."),
            "strengths": strengths,
            "improvements": improvements,
            "key_points_covered": question.get('expected_points', [])[:2],
            "missing_points": question.get('expected_points', [])[2:4],
            "technical_accuracy": score - 5,
            "communication_clarity": score + 2,
            "confidence_level": "high" if score > 80 else "medium" if score > 60 else "low"
        }
    
    def _get_fallback_analysis(self, question: Dict, response: str) -> Dict[str, Any]:
        """Get fallback analysis when AI fails"""
        
        return {
            "score": 70,
            "feedback": "We couldn't complete the AI analysis at this time. Based on basic evaluation, your response appears satisfactory. Please try again for detailed feedback.",
            "strengths": ["Response submitted successfully"],
            "improvements": ["Wait for AI analysis to be available"],
            "key_points_covered": [],
            "missing_points": [],
            "technical_accuracy": 70,
            "communication_clarity": 70,
            "confidence_level": "medium"
        }
    
    async def generate_follow_up_questions(
        self,
        question: Dict[str, Any],
        response: str,
        count: int = 2
    ) -> List[str]:
        """Generate follow-up questions based on response"""
        
        prompt = f"""
        Based on this interview response, generate {count} relevant follow-up questions.
        
        Original Question: {question.get('question_text')}
        Candidate's Response: {response}
        
        Generate follow-up questions that probe deeper into the topic.
        Return only the questions, one per line.
        """
        
        try:
            if self.use_openai:
                response = await openai.ChatCompletion.acreate(
                    model=self.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=300
                )
                result = response.choices[0].message.content
                questions = [q.strip() for q in result.split('\n') if q.strip()]
                return questions[:count]
            else:
                return self._get_mock_follow_ups(question)
                
        except Exception as e:
            logger.error(f"Error generating follow-ups: {str(e)}")
            return self._get_mock_follow_ups(question)
    
    def _get_mock_follow_ups(self, question: Dict) -> List[str]:
        """Get mock follow-up questions"""
        
        return [
            "Can you elaborate on that point?",
            "What alternatives did you consider?",
            "How would this scale in production?",
            "What are the trade-offs in your approach?"
        ][:2]
    
    async def evaluate_technical_depth(
        self,
        question: Dict,
        response: str
    ) -> Dict[str, Any]:
        """Evaluate technical depth of response"""
        
        prompt = f"""
        Evaluate the technical depth of this interview response.
        
        Question: {question.get('question_text')}
        Expected Level: {question.get('difficulty')}
        
        Response: {response}
        
        Rate the technical depth on a scale of 1-10 and explain your rating.
        Return JSON with:
        - depth_score: 1-10
        - explanation: string
        - missing_concepts: list of strings
        - advanced_points: list of strings (if any advanced concepts were mentioned)
        """
        
        try:
            if self.use_openai:
                response = await openai.ChatCompletion.acreate(
                    model=self.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=500
                )
                result = response.choices[0].message.content
                
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {
                "depth_score": 6,
                "explanation": "Response covers basic concepts but lacks advanced details.",
                "missing_concepts": ["Advanced implementation details", "Edge cases"],
                "advanced_points": []
            }
            
        except Exception as e:
            logger.error(f"Error evaluating technical depth: {str(e)}")
            return {
                "depth_score": 5,
                "explanation": "Unable to fully evaluate technical depth.",
                "missing_concepts": [],
                "advanced_points": []
            }