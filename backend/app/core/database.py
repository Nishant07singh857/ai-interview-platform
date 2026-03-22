"""
Firebase Database Integration
Complete implementation with all CRUD operations
"""

import firebase_admin
from firebase_admin import credentials, db, storage, auth
from firebase_admin import firestore
import json
import os
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import logging
from .config import settings

logger = logging.getLogger(__name__)

class FirebaseClient:
    """Firebase client wrapper with complete functionality"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.app = None
            self.db = None
            self.auth = None
            self.storage = None
            self.firestore_db = None
            self._initialized = True
    
    def initialize(self):
        """Initialize Firebase app with credentials"""
        try:
            if not firebase_admin._apps:
                # Check if credentials file exists
                if os.path.exists(settings.FIREBASE_CREDENTIALS):
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
                else:
                    # Try to load from environment variable
                    cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
                    if cred_json:
                        cred_dict = json.loads(cred_json)
                        cred = credentials.Certificate(cred_dict)
                    else:
                        raise FileNotFoundError(
                            f"Firebase credentials not found at {settings.FIREBASE_CREDENTIALS}"
                        )
                
                # Initialize the app
                self.app = firebase_admin.initialize_app(cred, {
                    'databaseURL': settings.FIREBASE_DATABASE_URL,
                    'storageBucket': settings.FIREBASE_STORAGE_BUCKET,
                    'projectId': settings.FIREBASE_PROJECT_ID
                })
                
                # Initialize services
                self.db = db
                self.auth = auth
                self.storage = storage
                self.firestore_db = firestore.client()
                
                logger.info("Firebase initialized successfully")
            else:
                self.app = firebase_admin.get_app()
                self.db = db
                self.auth = auth
                self.storage = storage
                self.firestore_db = firestore.client()
                
        except Exception as e:
            logger.error(f"Firebase initialization failed: {str(e)}")
            raise
    
    # Realtime Database Operations
    def get_reference(self, path: str):
        """Get database reference"""
        if not self.db:
            self.initialize()
        return self.db.reference(path)
    
    def get_data(self, path: str) -> Optional[Dict]:
        """Get data from path"""
        try:
            ref = self.get_reference(path)
            return ref.get()
        except Exception as e:
            logger.error(f"Error getting data from {path}: {str(e)}")
            return None
    
    def set_data(self, path: str, data: Dict) -> bool:
        """Set data at path"""
        try:
            ref = self.get_reference(path)
            ref.set(data)
            return True
        except Exception as e:
            logger.error(f"Error setting data at {path}: {str(e)}")
            return False
    
    def push_data(self, path: str, data: Dict) -> Optional[str]:
        """Push data (auto-generate key)"""
        try:
            ref = self.get_reference(path)
            new_ref = ref.push(data)
            return new_ref.key
        except Exception as e:
            logger.error(f"Error pushing data to {path}: {str(e)}")
            return None
    
    def update_data(self, path: str, data: Dict) -> bool:
        """Update data at path"""
        try:
            ref = self.get_reference(path)
            ref.update(data)
            return True
        except Exception as e:
            logger.error(f"Error updating data at {path}: {str(e)}")
            return False
    
    def delete_data(self, path: str) -> bool:
        """Delete data at path"""
        try:
            ref = self.get_reference(path)
            ref.delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting data at {path}: {str(e)}")
            return False
    
    # Firestore Operations
    def get_firestore_collection(self, collection_name: str):
        """Get Firestore collection"""
        if not self.firestore_db:
            self.initialize()
        return self.firestore_db.collection(collection_name)
    
    def add_firestore_document(self, collection: str, data: Dict) -> Optional[str]:
        """Add document to Firestore"""
        try:
            doc_ref = self.get_firestore_collection(collection).document()
            doc_ref.set({
                **data,
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP
            })
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error adding document to {collection}: {str(e)}")
            return None
    
    def get_firestore_document(self, collection: str, document_id: str) -> Optional[Dict]:
        """Get document from Firestore"""
        try:
            doc_ref = self.get_firestore_collection(collection).document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return {**doc.to_dict(), "id": doc.id}
            return None
        except Exception as e:
            logger.error(f"Error getting document from {collection}: {str(e)}")
            return None
    
    def query_firestore(self, collection: str, field: str, operator: str, value: Any) -> List[Dict]:
        """Query Firestore collection"""
        try:
            collection_ref = self.get_firestore_collection(collection)
            query = collection_ref.where(field, operator, value)
            results = []
            for doc in query.stream():
                results.append({**doc.to_dict(), "id": doc.id})
            return results
        except Exception as e:
            logger.error(f"Error querying {collection}: {str(e)}")
            return []
    
    # Authentication Operations
    def create_user(self, email: str, password: str, **kwargs) -> Optional[Dict]:
        """Create new user"""
        try:
            user = self.auth.create_user(
                email=email,
                password=password,
                **kwargs
            )
            return {
                "uid": user.uid,
                "email": user.email,
                "email_verified": user.email_verified
            }
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    def get_user(self, uid: str) -> Optional[Dict]:
        """Get user by UID"""
        try:
            user = self.auth.get_user(uid)
            return {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "photo_url": user.photo_url,
                "email_verified": user.email_verified,
                "disabled": user.disabled,
                "created_at": user.user_metadata.creation_timestamp
            }
        except Exception as e:
            logger.error(f"Error getting user {uid}: {str(e)}")
            return None
    
    def update_user(self, uid: str, **kwargs) -> bool:
        """Update user"""
        try:
            self.auth.update_user(uid, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Error updating user {uid}: {str(e)}")
            return False
    
    def delete_user(self, uid: str) -> bool:
        """Delete user"""
        try:
            self.auth.delete_user(uid)
            return True
        except Exception as e:
            logger.error(f"Error deleting user {uid}: {str(e)}")
            return False
    
    def verify_id_token(self, id_token: str) -> Optional[Dict]:
        """Verify Firebase ID token"""
        try:
            decoded_token = self.auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None
    
    # Storage Operations
    def upload_file(self, local_path: str, remote_path: str) -> Optional[str]:
        """Upload file to Firebase Storage"""
        try:
            bucket = self.storage.bucket()
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_path)
            
            # Make public and get URL
            blob.make_public()
            return blob.public_url
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return None
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from Firebase Storage"""
        try:
            bucket = self.storage.bucket()
            blob = bucket.blob(remote_path)
            blob.download_to_filename(local_path)
            return True
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """Delete file from Firebase Storage"""
        try:
            bucket = self.storage.bucket()
            blob = bucket.blob(remote_path)
            blob.delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def get_file_url(self, remote_path: str) -> Optional[str]:
        """Get public URL for file"""
        try:
            bucket = self.storage.bucket()
            blob = bucket.blob(remote_path)
            return blob.public_url
        except Exception as e:
            logger.error(f"Error getting file URL: {str(e)}")
            return None
    
    # Batch Operations
    def batch_write(self, operations: List[Dict]) -> bool:
        """Perform batch write operations"""
        try:
            batch = self.firestore_db.batch()
            
            for op in operations:
                if op["type"] == "set":
                    ref = self.firestore_db.collection(op["collection"]).document(op["document_id"])
                    batch.set(ref, op["data"])
                elif op["type"] == "update":
                    ref = self.firestore_db.collection(op["collection"]).document(op["document_id"])
                    batch.update(ref, op["data"])
                elif op["type"] == "delete":
                    ref = self.firestore_db.collection(op["collection"]).document(op["document_id"])
                    batch.delete(ref)
            
            batch.commit()
            return True
        except Exception as e:
            logger.error(f"Error in batch write: {str(e)}")
            return False
    
    # Transaction Operations
    def run_transaction(self, transaction_function):
        """Run a transaction"""
        try:
            return self.firestore_db.run_transaction(transaction_function)
        except Exception as e:
            logger.error(f"Error in transaction: {str(e)}")
            return None
    
    # Cleanup
    def close(self):
        """Close Firebase connections"""
        try:
            if self.app:
                firebase_admin.delete_app(self.app)
                logger.info("Firebase connections closed")
        except Exception as e:
            logger.error(f"Error closing Firebase: {str(e)}")

# Global instance
firebase_client = FirebaseClient()