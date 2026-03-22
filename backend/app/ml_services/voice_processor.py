from typing import List, Dict, Any, Optional

"""
Voice Processor - Speech-to-text and voice analysis service
"""

import speech_recognition as sr
from pydub import AudioSegment
import io
import logging
import re
from typing import Dict, Any, Optional
import tempfile
import os

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """Voice processing service for speech-to-text and analysis"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Filler words to detect
        self.filler_words = [
            'um', 'uh', 'like', 'you know', 'actually', 'basically',
            'literally', 'honestly', 'sort of', 'kind of', 'i mean'
        ]
    
    async def transcribe(self, audio_file_path: str) -> str:
        """Transcribe audio file to text"""
        
        try:
            # Convert to WAV if needed
            wav_path = await self._ensure_wav(audio_file_path)
            
            # Load audio file
            with sr.AudioFile(wav_path) as source:
                audio = self.recognizer.record(source)
                
                # Try different recognition engines
                text = await self._recognize_speech(audio)
                
                return text
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return ""
        finally:
            # Clean up temp files
            if wav_path != audio_file_path and os.path.exists(wav_path):
                os.remove(wav_path)
    
    async def _ensure_wav(self, file_path: str) -> str:
        """Convert audio file to WAV format if needed"""
        
        if file_path.endswith('.wav'):
            return file_path
        
        try:
            # Load audio with pydub
            audio = AudioSegment.from_file(file_path)
            
            # Create temp WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                wav_path = f.name
            
            # Export as WAV
            audio.export(wav_path, format='wav')
            
            return wav_path
            
        except Exception as e:
            logger.error(f"Error converting to WAV: {str(e)}")
            return file_path
    
    async def _recognize_speech(self, audio) -> str:
        """Recognize speech using multiple engines"""
        
        # Try Google Speech Recognition
        try:
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            logger.error(f"Google speech recognition error: {str(e)}")
        
        # Try Sphinx as fallback (offline)
        try:
            text = self.recognizer.recognize_sphinx(audio)
            return text
        except:
            pass
        
        return ""
    
    async def analyze(
        self,
        audio_file_path: str,
        transcript: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze voice for interview feedback"""
        
        # Get transcript if not provided
        if not transcript:
            transcript = await self.transcribe(audio_file_path)
        
        # Calculate speaking rate (words per minute)
        words = len(transcript.split())
        
        # Get audio duration
        duration = await self._get_audio_duration(audio_file_path)
        speaking_rate = (words / duration) * 60 if duration > 0 else 0
        
        # Detect filler words
        filler_word_count = 0
        filler_words_found = []
        
        transcript_lower = transcript.lower()
        for filler in self.filler_words:
            count = len(re.findall(r'\b' + re.escape(filler) + r'\b', transcript_lower))
            if count > 0:
                filler_word_count += count
                filler_words_found.append({
                    "word": filler,
                    "count": count
                })
        
        # Calculate clarity score (inverse of filler word density)
        clarity_score = 100 - (filler_word_count / words * 100) if words > 0 else 70
        clarity_score = max(0, min(100, clarity_score))
        
        # Analyze sentiment (simple heuristic)
        sentiment = await self._analyze_sentiment(transcript)
        
        # Check for key phrases
        key_phrases = await self._extract_key_phrases(transcript)
        
        # Simple grammar check (using regex patterns)
        grammar_issues = self._check_grammar(transcript)
        
        return {
            "transcript": transcript,
            "word_count": words,
            "duration_seconds": duration,
            "speaking_rate": round(speaking_rate, 1),
            "speaking_rate_category": self._categorize_speaking_rate(speaking_rate),
            "clarity_score": round(clarity_score, 1),
            "filler_word_count": filler_word_count,
            "filler_words": filler_words_found,
            "filler_word_density": round(filler_word_count / words * 100, 1) if words > 0 else 0,
            "sentiment": sentiment,
            "key_phrases": key_phrases[:5],
            "grammar_score": round(100 - len(grammar_issues) * 5, 1),
            "grammar_issues": grammar_issues,
            "confidence_score": self._calculate_confidence(transcript, speaking_rate)
        }
    
    async def _get_audio_duration(self, file_path: str) -> float:
        """Get audio duration in seconds"""
        
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0  # Convert to seconds
        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            return 60  # Default 60 seconds
    
    def _categorize_speaking_rate(self, rate: float) -> str:
        """Categorize speaking rate"""
        if rate < 100:
            return "slow"
        elif rate < 140:
            return "moderate"
        elif rate < 180:
            return "fast"
        else:
            return "very fast"
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        
        # Simple keyword-based sentiment analysis
        positive_words = [
            'excellent', 'great', 'good', 'positive', 'confident', 'sure',
            'definitely', 'absolutely', 'certainly', 'love', 'enjoy', 'excited'
        ]
        negative_words = [
            'bad', 'poor', 'terrible', 'awful', 'negative', 'unsure',
            'doubt', 'maybe', 'perhaps', 'difficult', 'hard', 'struggle'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        total = positive_count + negative_count
        
        if total == 0:
            sentiment_score = 0.5  # Neutral
        else:
            sentiment_score = positive_count / total
        
        if sentiment_score > 0.6:
            sentiment = "positive"
        elif sentiment_score < 0.4:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": round(sentiment_score, 2),
            "positive_count": positive_count,
            "negative_count": negative_count
        }
    
    async def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        
        # Simple noun phrase extraction
        import spacy
        
        try:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)
            
            phrases = []
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 4:  # Limit phrase length
                    phrases.append(chunk.text)
            
            return list(set(phrases))  # Remove duplicates
            
        except:
            # Fallback: just return sentences
            return [sent.strip() for sent in text.split('.') if sent.strip()][:5]
    
    def _check_grammar(self, text: str) -> List[str]:
        """Simple grammar checking"""
        
        issues = []
        
        # Check for common issues
        patterns = [
            (r'\b(i|we|they) (is)\b', 'Subject-verb agreement'),
            (r'\b(he|she|it) (are)\b', 'Subject-verb agreement'),
            (r'\b(a|an) ([aeiou])\b', 'Article usage'),
            (r'\b(their|there|they\'re)\b(?!\s*\w+\s*\1)', 'Word confusion'),
        ]
        
        text_lower = text.lower()
        for pattern, issue in patterns:
            if re.search(pattern, text_lower):
                issues.append(issue)
        
        return list(set(issues))  # Remove duplicates
    
    def _calculate_confidence(self, text: str, speaking_rate: float) -> int:
        """Calculate confidence score"""
        
        score = 70  # Base score
        
        # Speaking rate impact
        if 120 <= speaking_rate <= 160:
            score += 10  # Good pace
        elif speaking_rate < 100 or speaking_rate > 180:
            score -= 10  # Too slow or too fast
        
        # Word count impact
        words = len(text.split())
        if words < 20:
            score -= 10  # Too brief
        elif words > 200:
            score += 5   # Comprehensive
        
        # Check for hesitant language
        hesitant_words = ['maybe', 'perhaps', 'i think', 'sort of', 'kind of']
        for word in hesitant_words:
            if word in text.lower():
                score -= 2
        
        return max(0, min(100, score))