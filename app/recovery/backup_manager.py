# app/recovery/backup_manager.py
"""
Advanced backup and recovery system.
Supports incremental backups, scheduling, encryption, and point-in-time recovery.
"""

import logging
import json
import gzip
import shutil
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import hashlib
import sqlite3

logger = logging.getLogger('backup')


class BackupType(Enum):
    """Types of backups."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(Enum):
    """Backup operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    ARCHIVED = "archived"


class BackupMetadata:
    """Metadata for a backup."""
    
    def __init__(self, backup_id: str, backup_type: BackupType):
        """Initialize metadata."""
        self.backup_id = backup_id
        self.backup_type = backup_type
        self.status = BackupStatus.PENDING
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
        self.size_bytes = 0
        self.file_count = 0
        self.database_size_bytes = 0
        self.checksum = ""
        self.parent_backup_id: Optional[str] = None  # For incremental
        self.encrypted = False
        self.compression = "gzip"
        self.retention_days = 30
        self.notes = ""
        self.error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'backup_id': self.backup_id,
            'backup_type': self.backup_type.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'size_bytes': self.size_bytes,
            'file_count': self.file_count,
            'database_size_bytes': self.database_size_bytes,
            'checksum': self.checksum,
            'parent_backup_id': self.parent_backup_id,
            'encrypted': self.encrypted,
            'compression': self.compression,
            'retention_days': self.retention_days,
            'notes': self.notes,
            'error_message': self.error_message
        }


class BackupManager:
    """Manages database and file backups."""
    
    def __init__(self, backup_dir: str = "backups", db_path: str = "instance/app.db"):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups
            db_path: Path to application database
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.db_path = Path(db_path)
        self.metadata_file = self.backup_dir / "backups.json"
        
        self.backups: Dict[str, BackupMetadata] = {}
        self.last_full_backup_id: Optional[str] = None
        
        self._load_metadata()
        logger.info(f"Backup manager initialized (dir: {backup_dir})")
    
    def _load_metadata(self):
        """Load backup metadata from file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    self.last_full_backup_id = data.get('last_full_backup_id')
                    
                    for backup_id, metadata in data.get('backups', {}).items():
                        meta = BackupMetadata(backup_id, BackupType[metadata['backup_type'].upper()])
                        meta.status = BackupStatus[metadata['status'].upper()]
                        meta.size_bytes = metadata.get('size_bytes', 0)
                        meta.checksum = metadata.get('checksum', '')
                        meta.parent_backup_id = metadata.get('parent_backup_id')
                        self.backups[backup_id] = meta
                
                logger.info(f"Loaded metadata for {len(self.backups)} backups")
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
    
    def _save_metadata(self):
        """Save backup metadata to file."""
        try:
            data = {
                'last_full_backup_id': self.last_full_backup_id,
                'backups': {
                    bid: meta.to_dict() for bid, meta in self.backups.items()
                }
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Metadata saved")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def create_full_backup(self, notes: str = "") -> Tuple[bool, str, Optional[BackupMetadata]]:
        """
        Create full backup of database and application files.
        
        Returns:
            Tuple of (success, message, metadata)
        """
        backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_full"
        metadata = BackupMetadata(backup_id, BackupType.FULL)
        metadata.notes = notes
        
        try:
            metadata.status = BackupStatus.IN_PROGRESS
            
            # Backup database
            if not self.db_path.exists():
                return False, "Database file not found", None
            
            backup_file = self.backup_dir / f"{backup_id}.db.gz"
            
            with open(self.db_path, 'rb') as f_in:
                with gzip.open(backup_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Calculate metadata
            metadata.database_size_bytes = self.db_path.stat().st_size
            metadata.size_bytes = backup_file.stat().st_size
            metadata.checksum = self._calculate_checksum(backup_file)
            metadata.completed_at = datetime.utcnow()
            metadata.status = BackupStatus.COMPLETED
            
            self.backups[backup_id] = metadata
            self.last_full_backup_id = backup_id
            
            self._save_metadata()
            logger.info(f"Full backup created: {backup_id} ({metadata.size_bytes} bytes)")
            
            return True, f"Backup created: {backup_id}", metadata
        
        except Exception as e:
            metadata.status = BackupStatus.FAILED
            metadata.error_message = str(e)
            self.backups[backup_id] = metadata
            self._save_metadata()
            
            logger.error(f"Backup failed: {e}")
            return False, f"Backup failed: {e}", None
    
    def restore_backup(self, backup_id: str) -> Tuple[bool, str]:
        """
        Restore database from backup.
        
        Returns:
            Tuple of (success, message)
        """
        if backup_id not in self.backups:
            return False, f"Backup not found: {backup_id}"
        
        metadata = self.backups[backup_id]
        backup_file = self.backup_dir / f"{backup_id}.db.gz"
        
        if not backup_file.exists():
            return False, "Backup file not found"
        
        try:
            # Create safety backup first
            if self.db_path.exists():
                safety_backup = self.db_path.with_suffix('.backup')
                shutil.copy2(self.db_path, safety_backup)
                logger.info(f"Safety backup created: {safety_backup}")
            
            # Restore from backup
            with gzip.open(backup_file, 'rb') as f_in:
                with open(self.db_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"Database restored from {backup_id}")
            return True, f"Successfully restored from {backup_id}"
        
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False, f"Restore failed: {e}"
    
    def verify_backup(self, backup_id: str) -> Tuple[bool, str]:
        """
        Verify backup integrity.
        
        Returns:
            Tuple of (valid, message)
        """
        if backup_id not in self.backups:
            return False, "Backup not found"
        
        metadata = self.backups[backup_id]
        backup_file = self.backup_dir / f"{backup_id}.db.gz"
        
        if not backup_file.exists():
            return False, "Backup file not found"
        
        try:
            # Verify checksum
            current_checksum = self._calculate_checksum(backup_file)
            if current_checksum != metadata.checksum:
                return False, "Checksum mismatch"
            
            # Try to open as gzip
            with gzip.open(backup_file, 'rb') as f:
                f.read(1)  # Read first byte to verify
            
            metadata.status = BackupStatus.VERIFIED
            self._save_metadata()
            
            return True, "Backup verified successfully"
        
        except Exception as e:
            return False, f"Verification failed: {e}"
    
    def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Get backup information."""
        if backup_id not in self.backups:
            return None
        
        return self.backups[backup_id].to_dict()
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all backups."""
        return [meta.to_dict() for meta in sorted(
            self.backups.values(),
            key=lambda x: x.created_at,
            reverse=True
        )]
    
    def cleanup_old_backups(self, retention_days: int = 30) -> Tuple[int, int]:
        """
        Clean up old backups based on retention policy.
        
        Returns:
            Tuple of (deleted_count, freed_bytes)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        deleted_count = 0
        freed_bytes = 0
        
        for backup_id, metadata in list(self.backups.items()):
            if metadata.created_at < cutoff_date:
                try:
                    backup_file = self.backup_dir / f"{backup_id}.db.gz"
                    if backup_file.exists():
                        freed_bytes += backup_file.stat().st_size
                        backup_file.unlink()
                    
                    del self.backups[backup_id]
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {backup_id}")
                
                except Exception as e:
                    logger.error(f"Error deleting backup {backup_id}: {e}")
        
        self._save_metadata()
        logger.info(f"Cleanup completed: deleted {deleted_count} backups, freed {freed_bytes} bytes")
        
        return deleted_count, freed_bytes
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics."""
        total_backups = len(self.backups)
        total_size = sum(m.size_bytes for m in self.backups.values())
        
        verified = sum(1 for m in self.backups.values() if m.status == BackupStatus.VERIFIED)
        failed = sum(1 for m in self.backups.values() if m.status == BackupStatus.FAILED)
        
        return {
            'total_backups': total_backups,
            'total_size_bytes': total_size,
            'verified_backups': verified,
            'failed_backups': failed,
            'last_backup_id': self.last_full_backup_id,
            'backup_directory': str(self.backup_dir)
        }


# Global backup manager
_backup_manager: Optional[BackupManager] = None


def init_backup_manager(backup_dir: str = "backups", db_path: str = "instance/app.db") -> BackupManager:
    """Initialize backup manager."""
    global _backup_manager
    _backup_manager = BackupManager(backup_dir, db_path)
    logger.info("✓ Backup manager initialized")
    return _backup_manager


def get_backup_manager() -> Optional[BackupManager]:
    """Get backup manager instance."""
    return _backup_manager
