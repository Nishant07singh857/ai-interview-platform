"""
Model Loader - Centralized model loading and management
"""

import os
import joblib
import logging
from typing import Dict, Any, Optional
import torch
import tensorflow as tf
from transformers import AutoModel, AutoTokenizer
import spacy

logger = logging.getLogger(__name__)

class ModelLoader:
    """Centralized model loading and management"""
    
    _instance = None
    _models: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.models_loaded = False
    
    async def load_all_models(self):
        """Load all ML models"""
        try:
            # Load scikit-learn models
            await self._load_sklearn_models()
            
            # Load PyTorch models
            await self._load_pytorch_models()
            
            # Load TensorFlow models
            await self._load_tensorflow_models()
            
            # Load HuggingFace models
            await self._load_huggingface_models()
            
            # Load spaCy models
            await self._load_spacy_models()
            
            self.models_loaded = True
            logger.info("✅ All ML models loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {str(e)}")
            raise
    
    async def _load_sklearn_models(self):
        """Load scikit-learn models"""
        model_paths = {
            'skill_extractor': 'ml_services/models/skill_extractor.pkl',
            'difficulty_classifier': 'ml_services/models/difficulty_classifier.pkl',
            'readiness_predictor': 'ml_services/models/readiness_predictor.pkl',
            'topic_classifier': 'ml_services/models/topic_classifier.pkl',
            'sentiment_analyzer': 'ml_services/models/sentiment_analyzer.pkl'
        }
        
        for name, path in model_paths.items():
            if os.path.exists(path):
                try:
                    self._models[name] = joblib.load(path)
                    logger.info(f"  ✅ Loaded {name}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Failed to load {name}: {str(e)}")
                    self._models[name] = None
            else:
                logger.warning(f"  ⚠️ Model not found: {path}")
                self._models[name] = None
    
    async def _load_pytorch_models(self):
        """Load PyTorch models"""
        model_paths = {
            'answer_evaluator': 'ml_services/models/answer_evaluator.pt',
            'code_analyzer': 'ml_services/models/code_analyzer.pt'
        }
        
        for name, path in model_paths.items():
            if os.path.exists(path):
                try:
                    self._models[name] = torch.load(path, map_location='cpu')
                    self._models[name].eval()
                    logger.info(f"  ✅ Loaded {name}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Failed to load {name}: {str(e)}")
                    self._models[name] = None
            else:
                logger.warning(f"  ⚠️ Model not found: {path}")
                self._models[name] = None
    
    async def _load_tensorflow_models(self):
        """Load TensorFlow models"""
        model_paths = {
            'face_analyzer': 'ml_services/models/face_analyzer',
            'gesture_detector': 'ml_services/models/gesture_detector'
        }
        
        for name, path in model_paths.items():
            if os.path.exists(path):
                try:
                    self._models[name] = tf.keras.models.load_model(path)
                    logger.info(f"  ✅ Loaded {name}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Failed to load {name}: {str(e)}")
                    self._models[name] = None
            else:
                logger.warning(f"  ⚠️ Model not found: {path}")
                self._models[name] = None
    
    async def _load_huggingface_models(self):
        """Load HuggingFace models"""
        try:
            # Load transformer models
            model_name = "microsoft/deberta-v3-base"
            self._models['transformer_tokenizer'] = AutoTokenizer.from_pretrained(model_name)
            self._models['transformer_model'] = AutoModel.from_pretrained(model_name)
            logger.info(f"  ✅ Loaded HuggingFace model: {model_name}")
        except Exception as e:
            logger.warning(f"  ⚠️ Failed to load HuggingFace model: {str(e)}")
            self._models['transformer_tokenizer'] = None
            self._models['transformer_model'] = None
    
    async def _load_spacy_models(self):
        """Load spaCy models"""
        try:
            self._models['spacy_nlp'] = spacy.load("en_core_web_lg")
            logger.info("  ✅ Loaded spaCy model: en_core_web_lg")
        except Exception as e:
            try:
                # Try smaller model
                self._models['spacy_nlp'] = spacy.load("en_core_web_md")
                logger.info("  ✅ Loaded spaCy model: en_core_web_md")
            except:
                logger.warning(f"  ⚠️ Failed to load spaCy model: {str(e)}")
                self._models['spacy_nlp'] = None
    
    def get_model(self, name: str) -> Optional[Any]:
        """Get a loaded model by name"""
        return self._models.get(name)
    
    async def unload_models(self):
        """Unload all models to free memory"""
        self._models.clear()
        self.models_loaded = False
        logger.info("All models unloaded")

# Global instance
model_loader = ModelLoader()