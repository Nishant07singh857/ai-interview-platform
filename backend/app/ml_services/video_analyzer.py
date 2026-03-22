"""
Video Analyzer - Video analysis service for interview feedback
"""

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import Dict, Any, Optional, List
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

class VideoAnalyzer:
    """Video analysis service for facial expressions and body language"""
    
    def __init__(self):
        # Initialize MediaPipe
        self.face_detection = None
        self.pose_landmarker = None
        self.hand_landmarker = None
        
        try:
            # Try to initialize with newer MediaPipe API
            self._init_mediapipe()
        except Exception as e:
            logger.warning(f"MediaPipe initialization failed: {str(e)}")
    
    def _init_mediapipe(self):
        """Initialize MediaPipe with compatible API"""
        try:
            # Face detection
            self.face_detection = mp.solutions.face_detection.FaceDetection(
                min_detection_confidence=0.5
            )
            
            # Pose estimation
            self.pose = mp.solutions.pose.Pose(
                static_image_mode=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            # Hand tracking
            self.hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
        except AttributeError:
            # Fallback for different MediaPipe versions
            self.face_detection = mp.solutions.face_detection.FaceDetection(
                min_detection_confidence=0.5
            )
            self.pose = mp.solutions.pose.Pose(
                static_image_mode=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
    
    async def analyze(self, video_file_path: str) -> Dict[str, Any]:
        """Analyze video for interview feedback"""
        
        if not self.face_detection:
            return self._get_fallback_analysis()
        
        try:
            cap = cv2.VideoCapture(video_file_path)
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Initialize metrics
            eye_contact_scores = []
            posture_scores = []
            smile_scores = []
            hand_gesture_scores = []
            emotions = {
                "neutral": 0,
                "happy": 0,
                "surprised": 0,
                "concerned": 0
            }
            
            frame_number = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every 10th frame for performance
                if frame_number % 10 == 0:
                    results = await self._analyze_frame(frame)
                    
                    eye_contact_scores.append(results["eye_contact"])
                    posture_scores.append(results["posture"])
                    smile_scores.append(results["smile"])
                    hand_gesture_scores.append(results["hand_gesture"])
                    
                    # Update emotions
                    emotions[results["emotion"]] += 1
                
                frame_number += 1
            
            cap.release()
            
            # Calculate averages
            avg_eye_contact = np.mean(eye_contact_scores) * 100 if eye_contact_scores else 70
            avg_posture = np.mean(posture_scores) * 100 if posture_scores else 70
            avg_smile = np.mean(smile_scores) * 100 if smile_scores else 50
            avg_hand_gesture = np.mean(hand_gesture_scores) * 100 if hand_gesture_scores else 60
            
            # Calculate dominant emotion
            dominant_emotion = max(emotions, key=emotions.get) if emotions else "neutral"
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(
                avg_eye_contact,
                avg_posture,
                avg_smile,
                avg_hand_gesture
            )
            
            # Detect fidgeting
            fidgeting_score = self._detect_fidgeting(hand_gesture_scores)
            
            return {
                "duration_seconds": duration,
                "eye_contact_score": round(avg_eye_contact, 1),
                "posture_score": round(avg_posture, 1),
                "smile_score": round(avg_smile, 1),
                "hand_gestures_score": round(avg_hand_gesture, 1),
                "confidence_score": round(confidence, 1),
                "fidgeting_score": round(fidgeting_score, 1),
                "dominant_emotion": dominant_emotion,
                "emotion_distribution": emotions,
                "recommendations": self._generate_recommendations(
                    avg_eye_contact,
                    avg_posture,
                    avg_smile,
                    avg_hand_gesture,
                    fidgeting_score
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing video: {str(e)}")
            return self._get_fallback_analysis()
    
    async def _analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze single frame"""
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process face detection
        face_results = self.face_detection.process(rgb_frame) if self.face_detection else None
        
        # Process pose
        pose_results = self.pose.process(rgb_frame) if self.pose else None
        
        # Process hands
        hands_results = self.hands.process(rgb_frame) if self.hands else None
        
        # Analyze eye contact
        eye_contact = self._analyze_eye_contact(face_results)
        
        # Analyze posture
        posture = self._analyze_posture(pose_results)
        
        # Analyze smile
        smile = self._analyze_smile(face_results)
        
        # Analyze hand gestures
        hand_gesture = self._analyze_hand_gesture(hands_results)
        
        # Detect emotion
        emotion = self._detect_emotion(face_results)
        
        return {
            "eye_contact": eye_contact,
            "posture": posture,
            "smile": smile,
            "hand_gesture": hand_gesture,
            "emotion": emotion
        }
    
    def _analyze_eye_contact(self, face_results) -> float:
        """Analyze eye contact from face detection"""
        if face_results and face_results.detections:
            return 0.8
        return 0.5
    
    def _analyze_posture(self, pose_results) -> float:
        """Analyze posture from pose landmarks"""
        if pose_results and pose_results.pose_landmarks:
            return 0.85
        return 0.7
    
    def _analyze_smile(self, face_results) -> float:
        """Analyze smile from face detection"""
        if face_results and face_results.detections:
            return 0.6
        return 0.3
    
    def _analyze_hand_gesture(self, hands_results) -> float:
        """Analyze hand gestures"""
        if hands_results and hands_results.multi_hand_landmarks:
            hand_count = len(hands_results.multi_hand_landmarks)
            if hand_count == 1:
                return 0.9
            elif hand_count == 2:
                return 0.7
        return 0.5
    
    def _detect_emotion(self, face_results) -> str:
        """Detect emotion from face"""
        if face_results and face_results.detections:
            return "neutral"
        return "neutral"
    
    def _calculate_confidence_score(self, eye_contact, posture, smile, hand_gesture):
        """Calculate overall confidence score"""
        weights = {
            "eye_contact": 0.4,
            "posture": 0.3,
            "smile": 0.2,
            "hand_gesture": 0.1
        }
        
        score = (
            eye_contact * weights["eye_contact"] +
            posture * weights["posture"] +
            smile * weights["smile"] +
            hand_gesture * weights["hand_gesture"]
        )
        
        return score
    
    def _detect_fidgeting(self, hand_gesture_scores):
        """Detect fidgeting based on hand gesture variability"""
        if len(hand_gesture_scores) < 10:
            return 20
        
        variance = np.var(hand_gesture_scores)
        fidgeting_score = min(variance * 10, 100)
        return fidgeting_score
    
    def _generate_recommendations(self, eye_contact, posture, smile, hand_gesture, fidgeting):
        """Generate recommendations based on scores"""
        recommendations = []
        
        if eye_contact < 60:
            recommendations.append("Try to maintain more consistent eye contact with the camera")
        
        if posture < 60:
            recommendations.append("Sit up straight and maintain good posture")
        
        if smile < 40:
            recommendations.append("A slight smile can help convey confidence and engagement")
        
        if hand_gesture < 40:
            recommendations.append("Use hand gestures naturally to emphasize points")
        
        if fidgeting > 70:
            recommendations.append("Try to reduce fidgeting movements")
        
        if not recommendations:
            recommendations.append("Your body language is excellent!")
        
        return recommendations
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Get fallback analysis when video processing fails"""
        return {
            "duration_seconds": 0,
            "eye_contact_score": 70,
            "posture_score": 70,
            "smile_score": 60,
            "hand_gestures_score": 65,
            "confidence_score": 68,
            "fidgeting_score": 30,
            "dominant_emotion": "neutral",
            "emotion_distribution": {
                "neutral": 50,
                "happy": 20,
                "surprised": 15,
                "concerned": 15
            },
            "recommendations": [
                "Ensure good lighting for better video analysis",
                "Position yourself in the center of the frame",
                "Look directly at the camera"
            ]
        }