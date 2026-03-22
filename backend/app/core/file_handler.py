"""
File Handler - File upload validation and handling
"""

import os
import magic
import hashlib
from typing import Optional, BinaryIO, Tuple
from pathlib import Path
import logging
from fastapi import UploadFile, HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

class FileHandler:
    """File handling service for uploads"""
    
    ALLOWED_MIME_TYPES = {
        '.pdf': {'application/pdf', 'application/octet-stream'},
        '.docx': {
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/zip',
            'application/octet-stream',
        },
        '.txt': {'text/plain', 'application/octet-stream'},
        '.jpg': {'image/jpeg'},
        '.jpeg': {'image/jpeg'},
        '.png': {'image/png'},
    }
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_PATH)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = settings.MAX_UPLOAD_SIZE
    
    async def validate_file(self, file: UploadFile, allowed_types: Optional[list] = None) -> bool:
        """Validate file type and size"""
        
        # Check file size
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > self.max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {self.max_size / 1024 / 1024:.1f}MB"
            )
        
        # Check file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type {ext} not allowed"
            )
        
        # Read first few bytes for magic number check
        content = await file.read(2048)
        await file.seek(0)
        
        # Check magic number
        mime = magic.from_buffer(content, mime=True)
        expected_mimes = self.ALLOWED_MIME_TYPES[ext]
        
        if mime not in expected_mimes and not mime.startswith('text/'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file content. Expected {', '.join(sorted(expected_mimes))}, got {mime}"
            )
        
        return True
    
    async def save_file(self, file: UploadFile, subdir: str = "") -> Tuple[str, str]:
        """Save file to disk and return path and URL"""
        
        # Create subdirectory
        save_dir = self.upload_dir / subdir
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        content = await file.read()
        file_hash = hashlib.md5(content).hexdigest()
        ext = os.path.splitext(file.filename)[1]
        filename = f"{file_hash}{ext}"
        
        # Save file
        file_path = save_dir / filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Reset file position
        await file.seek(0)
        
        # Return relative path and URL
        relative_path = str(Path(subdir) / filename)
        url = f"/uploads/{relative_path}"
        
        logger.info(f"File saved: {relative_path}")
        return relative_path, url
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from disk"""
        try:
            full_path = self.upload_dir / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False
    
    def get_file_path(self, file_path: str) -> Path:
        """Get full file path"""
        return self.upload_dir / file_path

# Global instance
file_handler = FileHandler()
