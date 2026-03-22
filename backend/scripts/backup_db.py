#!/usr/bin/env python3
"""
Database Backup Script
Run: python -m scripts.backup_db
"""

import asyncio
import json
import os
import sys
from datetime import datetime
import logging
import gzip
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import firebase_client
from app.core.storage import storage_service
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Database backup utility"""
    
    def __init__(self):
        self.firebase = firebase_client
        self.storage = storage_service
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    async def create_backup(self, compress: bool = True) -> dict:
        """Create a complete database backup"""
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_id = f"backup_{timestamp}"
        
        logger.info(f"📦 Creating backup: {backup_id}")
        
        backup_data = {
            "metadata": {
                "backup_id": backup_id,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0",
                "environment": settings.ENVIRONMENT
            },
            "collections": {}
        }
        
        # Define collections to backup
        collections = [
            "users",
            "questions",
            "companies",
            "topics",
            "badges",
            "interview_templates",
            "company_grids",
            "forums",
            "threads",
            "posts"
        ]
        
        for collection in collections:
            logger.info(f"  Backing up {collection}...")
            data = self.firebase.get_data(collection) or {}
            backup_data["collections"][collection] = data
        
        # Save to file
        backup_file = self.backup_dir / f"{backup_id}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        # Compress if requested
        if compress:
            compressed_file = self.backup_dir / f"{backup_id}.json.gz"
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed file
            backup_file.unlink()
            final_file = compressed_file
            size = compressed_file.stat().st_size
        else:
            final_file = backup_file
            size = backup_file.stat().st_size
        
        # Upload to cloud storage
        storage_path = f"backups/{final_file.name}"
        with open(final_file, 'rb') as f:
            url = await self.storage.upload_file(
                f.read(),
                storage_path,
                "application/gzip" if compress else "application/json"
            )
        
        logger.info(f"✅ Backup created: {final_file.name} ({size / 1024 / 1024:.2f} MB)")
        logger.info(f"   Storage URL: {url}")
        
        # Clean up old backups
        await self.cleanup_old_backups()
        
        return {
            "backup_id": backup_id,
            "file": final_file.name,
            "size": size,
            "url": url,
            "collections": len(collections),
            "timestamp": backup_data["metadata"]["timestamp"]
        }
    
    async def restore_backup(self, backup_id: str) -> bool:
        """Restore from a backup"""
        
        backup_file = self.backup_dir / f"{backup_id}.json"
        compressed_file = self.backup_dir / f"{backup_id}.json.gz"
        
        if compressed_file.exists():
            # Decompress
            with gzip.open(compressed_file, 'rb') as f_in:
                data = json.loads(f_in.read().decode('utf-8'))
        elif backup_file.exists():
            with open(backup_file, 'r') as f:
                data = json.load(f)
        else:
            logger.error(f"Backup {backup_id} not found")
            return False
        
        logger.info(f"📦 Restoring backup: {backup_id}")
        
        # Verify backup
        if data.get("metadata", {}).get("backup_id") != backup_id:
            logger.error("Backup verification failed")
            return False
        
        # Restore collections
        for collection, collection_data in data["collections"].items():
            logger.info(f"  Restoring {collection}...")
            
            # Clear existing data
            existing = self.firebase.get_data(collection) or {}
            for key in existing:
                self.firebase.delete_data(f"{collection}/{key}")
            
            # Restore data
            for key, value in collection_data.items():
                self.firebase.set_data(f"{collection}/{key}", value)
        
        logger.info("✅ Backup restored successfully")
        return True
    
    async def list_backups(self) -> list:
        """List available backups"""
        
        backups = []
        
        # Local backups
        for file in self.backup_dir.glob("backup_*.json*"):
            stats = file.stat()
            backups.append({
                "name": file.name,
                "size": stats.st_size,
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "location": "local"
            })
        
        # Cloud backups
        cloud_files = self.storage.list_files("backups/")
        for file in cloud_files:
            backups.append({
                "name": file["name"],
                "size": file["size"],
                "modified": file["updated"],
                "location": "cloud"
            })
        
        # Sort by date (newest first)
        backups.sort(key=lambda x: x["name"], reverse=True)
        
        return backups
    
    async def cleanup_old_backups(self, keep_days: int = 7, keep_count: int = 10):
        """Delete old backups"""
        
        backups = await self.list_backups()
        
        # Group by location
        local_backups = [b for b in backups if b["location"] == "local"]
        cloud_backups = [b for b in backups if b["location"] == "cloud"]
        
        # Keep only recent backups
        for backup_list, location in [(local_backups, "local"), (cloud_backups, "cloud")]:
            if len(backup_list) > keep_count:
                to_delete = backup_list[keep_count:]
                for backup in to_delete:
                    try:
                        if location == "local":
                            (self.backup_dir / backup["name"]).unlink()
                        else:
                            self.storage.delete_file(f"backups/{backup['name']}")
                        logger.info(f"  Deleted old backup: {backup['name']}")
                    except Exception as e:
                        logger.error(f"  Failed to delete {backup['name']}: {e}")
    
    async def verify_backup(self, backup_id: str) -> dict:
        """Verify backup integrity"""
        
        backup_file = self.backup_dir / f"{backup_id}.json"
        compressed_file = self.backup_dir / f"{backup_id}.json.gz"
        
        if compressed_file.exists():
            with gzip.open(compressed_file, 'rb') as f_in:
                data = json.loads(f_in.read().decode('utf-8'))
        elif backup_file.exists():
            with open(backup_file, 'r') as f:
                data = json.load(f)
        else:
            return {"valid": False, "error": "Backup not found"}
        
        # Verify metadata
        if "metadata" not in data:
            return {"valid": False, "error": "Missing metadata"}
        
        if "collections" not in data:
            return {"valid": False, "error": "Missing collections"}
        
        # Count total items
        total_items = sum(len(coll) for coll in data["collections"].values())
        
        return {
            "valid": True,
            "backup_id": data["metadata"]["backup_id"],
            "timestamp": data["metadata"]["timestamp"],
            "collections": len(data["collections"]),
            "total_items": total_items,
            "version": data["metadata"].get("version", "unknown")
        }

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database backup utility")
    parser.add_argument("action", choices=["create", "restore", "list", "verify", "cleanup"],
                       help="Action to perform")
    parser.add_argument("--backup-id", help="Backup ID for restore/verify")
    parser.add_argument("--no-compress", action="store_true", help="Don't compress backup")
    parser.add_argument("--keep-days", type=int, default=7, help="Days to keep backups")
    parser.add_argument("--keep-count", type=int, default=10, help="Number of backups to keep")
    
    args = parser.parse_args()
    
    backup = DatabaseBackup()
    
    if args.action == "create":
        result = await backup.create_backup(compress=not args.no_compress)
        print(f"\nBackup created successfully:")
        print(f"  ID: {result['backup_id']}")
        print(f"  File: {result['file']}")
        print(f"  Size: {result['size'] / 1024 / 1024:.2f} MB")
        print(f"  Collections: {result['collections']}")
        print(f"  URL: {result['url']}")
    
    elif args.action == "restore":
        if not args.backup_id:
            print("Error: --backup-id required for restore")
            return
        success = await backup.restore_backup(args.backup_id)
        if success:
            print(f"✅ Backup {args.backup_id} restored successfully")
    
    elif args.action == "list":
        backups = await backup.list_backups()
        print(f"\nAvailable backups ({len(backups)}):")
        for b in backups:
            size_mb = b['size'] / 1024 / 1024
            print(f"  {b['name']} - {size_mb:.2f} MB - {b['location']} - {b['modified']}")
    
    elif args.action == "verify":
        if not args.backup_id:
            print("Error: --backup-id required for verify")
            return
        result = await backup.verify_backup(args.backup_id)
        if result["valid"]:
            print(f"\n✅ Backup {args.backup_id} is valid:")
            print(f"  Timestamp: {result['timestamp']}")
            print(f"  Collections: {result['collections']}")
            print(f"  Total items: {result['total_items']}")
            print(f"  Version: {result['version']}")
        else:
            print(f"❌ Backup invalid: {result.get('error')}")
    
    elif args.action == "cleanup":
        await backup.cleanup_old_backups(args.keep_days, args.keep_count)
        print(f"✅ Cleaned up old backups")

if __name__ == "__main__":
    asyncio.run(main())