"""
Storage Service - File storage handling (local/S3/Firebase)
"""

import os
import logging
import aiofiles
from typing import Optional, BinaryIO, Union
from datetime import datetime, timedelta
import mimetypes
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    logger.warning("boto3 not installed. AWS S3 storage will not be available.")

try:
    from google.cloud import storage as gcs
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    logger.warning("google-cloud-storage not installed. GCS storage will not be available.")

class StorageService:
    """Storage service for file uploads and downloads"""
    
    def __init__(self):
        self.storage_type = "local"  # local, s3, gcs, firebase
        self._init_storage()
    
    def _init_storage(self):
        """Initialize storage backend"""
        # Check if we should use S3
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and AWS_AVAILABLE:
            self.storage_type = "s3"
            self._init_s3()
        # Check if we should use GCS
        elif settings.GCS_BUCKET and GCS_AVAILABLE:
            self.storage_type = "gcs"
            self._init_gcs()
        else:
            self.storage_type = "local"
            self._init_local()
        
        logger.info(f"Storage initialized with type: {self.storage_type}")
    
    def _init_s3(self):
        """Initialize S3 client"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.s3_bucket = settings.AWS_S3_BUCKET
            logger.info(f"S3 initialized with bucket: {self.s3_bucket}")
        except Exception as e:
            logger.error(f"Failed to initialize S3: {str(e)}")
            self.storage_type = "local"
            self._init_local()
    
    def _init_gcs(self):
        """Initialize Google Cloud Storage client"""
        try:
            self.gcs_client = gcs.Client()
            self.gcs_bucket = self.gcs_client.bucket(settings.GCS_BUCKET)
            logger.info(f"GCS initialized with bucket: {settings.GCS_BUCKET}")
        except Exception as e:
            logger.error(f"Failed to initialize GCS: {str(e)}")
            self.storage_type = "local"
            self._init_local()
    
    def _init_local(self):
        """Initialize local storage"""
        self.local_path = Path(settings.UPLOAD_PATH)
        self.local_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage initialized at: {self.local_path}")
    
    async def upload_file(
        self,
        file_data: Union[bytes, BinaryIO],
        file_path: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """Upload file to storage and return URL"""
        
        if self.storage_type == "s3":
            return await self._upload_to_s3(file_data, file_path, content_type, metadata)
        elif self.storage_type == "gcs":
            return await self._upload_to_gcs(file_data, file_path, content_type, metadata)
        else:
            return await self._upload_to_local(file_data, file_path, content_type)
    
    async def _upload_to_s3(self, file_data, file_path, content_type, metadata) -> str:
        """Upload to S3"""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            if metadata:
                extra_args['Metadata'] = metadata
            
            if isinstance(file_data, bytes):
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=file_path,
                    Body=file_data,
                    **extra_args
                )
            else:
                self.s3_client.upload_fileobj(
                    file_data,
                    self.s3_bucket,
                    file_path,
                    ExtraArgs=extra_args
                )
            
            # Generate URL
            url = f"https://{self.s3_bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{file_path}"
            return url
            
        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise
    
    async def _upload_to_gcs(self, file_data, file_path, content_type, metadata) -> str:
        """Upload to Google Cloud Storage"""
        try:
            blob = self.gcs_bucket.blob(file_path)
            
            if metadata:
                blob.metadata = metadata
            
            if isinstance(file_data, bytes):
                blob.upload_from_string(file_data, content_type=content_type)
            else:
                blob.upload_from_file(file_data, content_type=content_type)
            
            # Make public
            blob.make_public()
            return blob.public_url
            
        except Exception as e:
            logger.error(f"GCS upload error: {str(e)}")
            raise
    
    async def _upload_to_local(self, file_data, file_path, content_type) -> str:
        """Upload to local filesystem"""
        try:
            full_path = self.local_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(file_data, bytes):
                async with aiofiles.open(full_path, 'wb') as f:
                    await f.write(file_data)
            else:
                async with aiofiles.open(full_path, 'wb') as f:
                    chunk = file_data.read(8192)
                    while chunk:
                        await f.write(chunk)
                        chunk = file_data.read(8192)
            
            # Return local URL
            return f"/uploads/{file_path}"
            
        except Exception as e:
            logger.error(f"Local upload error: {str(e)}")
            raise
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from storage"""
        
        if self.storage_type == "s3":
            return await self._download_from_s3(file_path)
        elif self.storage_type == "gcs":
            return await self._download_from_gcs(file_path)
        else:
            return await self._download_from_local(file_path)
    
    async def _download_from_s3(self, file_path: str) -> bytes:
        """Download from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=file_path
            )
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"S3 download error: {str(e)}")
            raise
    
    async def _download_from_gcs(self, file_path: str) -> bytes:
        """Download from GCS"""
        try:
            blob = self.gcs_bucket.blob(file_path)
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"GCS download error: {str(e)}")
            raise
    
    async def _download_from_local(self, file_path: str) -> bytes:
        """Download from local filesystem"""
        try:
            full_path = self.local_path / file_path
            async with aiofiles.open(full_path, 'rb') as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Local download error: {str(e)}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        
        try:
            if self.storage_type == "s3":
                self.s3_client.delete_object(
                    Bucket=self.s3_bucket,
                    Key=file_path
                )
            elif self.storage_type == "gcs":
                blob = self.gcs_bucket.blob(file_path)
                blob.delete()
            else:
                full_path = self.local_path / file_path
                if full_path.exists():
                    full_path.unlink()
            
            return True
            
        except Exception as e:
            logger.error(f"Delete error: {str(e)}")
            return False
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get temporary signed URL for file"""
        
        try:
            if self.storage_type == "s3":
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.s3_bucket,
                        'Key': file_path
                    },
                    ExpiresIn=expires_in
                )
                return url
                
            elif self.storage_type == "gcs":
                blob = self.gcs_bucket.blob(file_path)
                url = blob.generate_signed_url(
                    expiration=timedelta(seconds=expires_in)
                )
                return url
                
            else:
                # Local files don't need signed URLs
                return f"/uploads/{file_path}"
                
        except Exception as e:
            logger.error(f"URL generation error: {str(e)}")
            return None
    
    async def list_files(self, prefix: str = "") -> list:
        """List files in storage"""
        
        files = []
        
        try:
            if self.storage_type == "s3":
                paginator = self.s3_client.get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=self.s3_bucket, Prefix=prefix):
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            files.append({
                                'name': obj['Key'],
                                'size': obj['Size'],
                                'modified': obj['LastModified'].isoformat()
                            })
                            
            elif self.storage_type == "gcs":
                blobs = self.gcs_bucket.list_blobs(prefix=prefix)
                for blob in blobs:
                    files.append({
                        'name': blob.name,
                        'size': blob.size,
                        'modified': blob.updated.isoformat() if blob.updated else None
                    })
                    
            else:
                path = self.local_path / prefix
                if path.exists():
                    for item in path.iterdir():
                        if item.is_file():
                            stat = item.stat()
                            files.append({
                                'name': str(item.relative_to(self.local_path)),
                                'size': stat.st_size,
                                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                            })
            
            return files
            
        except Exception as e:
            logger.error(f"List files error: {str(e)}")
            return []

# Global instance
storage_service = StorageService()