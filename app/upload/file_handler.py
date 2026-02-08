# app/upload/file_handler.py
"""
Secure file upload handling and validation.
Provides safe file upload with virus scanning simulation.
"""

import os
import logging
import mimetypes
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
from datetime import datetime
import hashlib
import magic

logger = logging.getLogger('upload')


class FileUploadConfig:
    """File upload configuration."""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'document': {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx'},
        'image': {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'},
        'archive': {'zip', 'tar', 'gz', 'rar'},
        'video': {'mp4', 'avi', 'mov', 'mkv'},
        'audio': {'mp3', 'wav', 'flac', 'aac'}
    }
    
    # Max file size (5MB default)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    # Upload directory
    UPLOAD_DIR = os.path.join('uploads', 'user_files')
    
    # Quarantine directory for suspicious files
    QUARANTINE_DIR = os.path.join('uploads', 'quarantine')
    
    # Allowed MIME types
    ALLOWED_MIMES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'application/zip',
        'application/x-tar',
        'video/mp4',
        'audio/mpeg',
        'text/plain',
        'application/json'
    }
    
    # Dangerous extensions to block
    DANGEROUS_EXTENSIONS = {
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar',
        'zip', 'rar', '7z', 'app', 'bin', 'dll', 'so', 'dylib'
    }


class FileUploadValidator:
    """Validate uploaded files."""
    
    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, str]:
        """
        Validate filename for security.
        
        Args:
            filename: Original filename
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename or len(filename) == 0:
            return False, "Filename is empty"
        
        # Check length
        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"
        
        # Check for directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Filename contains invalid characters"
        
        # Check for null bytes
        if '\x00' in filename:
            return False, "Filename contains null bytes"
        
        # Get extension
        _, ext = os.path.splitext(filename)
        ext = ext.lstrip('.').lower()
        
        # Check extension
        if ext in FileUploadConfig.DANGEROUS_EXTENSIONS:
            return False, f"File type '.{ext}' is not allowed"
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        
        if mime_type and mime_type not in FileUploadConfig.ALLOWED_MIMES:
            return False, f"MIME type '{mime_type}' is not allowed"
        
        return True, ""
    
    @staticmethod
    def validate_file_size(file_size: int) -> Tuple[bool, str]:
        """
        Validate file size.
        
        Args:
            file_size: File size in bytes
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if file_size == 0:
            return False, "File is empty"
        
        if file_size > FileUploadConfig.MAX_FILE_SIZE:
            max_mb = FileUploadConfig.MAX_FILE_SIZE // (1024 * 1024)
            return False, f"File too large (max {max_mb}MB)"
        
        return True, ""
    
    @staticmethod
    def validate_file_content(file_path: str, expected_type: str = 'document') -> Tuple[bool, str]:
        """
        Validate file content using magic bytes.
        
        Args:
            file_path: Path to uploaded file
            expected_type: Expected file type category
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check magic bytes using python-magic
            mime_type = magic.from_file(file_path, mime=True)
            
            if mime_type not in FileUploadConfig.ALLOWED_MIMES:
                logger.warning(f"Blocked upload: Invalid MIME type {mime_type}")
                return False, f"Invalid file type detected: {mime_type}"
            
            return True, ""
        except ImportError:
            # Fallback if python-magic not available
            logger.debug("python-magic not available, skipping magic byte check")
            return True, ""
        except Exception as e:
            logger.error(f"Error validating file content: {str(e)}")
            return False, "Could not validate file content"
    
    @staticmethod
    def scan_for_threats(file_path: str) -> Tuple[bool, str]:
        """
        Scan file for potential threats (virus simulation).
        
        Args:
            file_path: Path to file to scan
        
        Returns:
            Tuple of (is_safe, threat_message)
        """
        # In production, would use antivirus API (ClamAV, VirusTotal, etc.)
        # For now, just do basic checks
        
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Check for suspiciously large files
        if file_size > 50 * 1024 * 1024:  # 50MB
            logger.warning(f"Suspicious: Large file uploaded: {filename} ({file_size} bytes)")
            return False, "File is suspiciously large"
        
        # In production, would call antivirus API here
        # For now, assume safe
        logger.debug(f"File scan passed: {filename}")
        return True, ""


class FileUploadHandler:
    """Handle secure file uploads."""
    
    def __init__(self, upload_dir: str = None):
        """Initialize handler."""
        self.upload_dir = upload_dir or FileUploadConfig.UPLOAD_DIR
        self.quarantine_dir = FileUploadConfig.QUARANTINE_DIR
        
        # Create directories
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.quarantine_dir, exist_ok=True)
    
    def handle_upload(self, file_obj, user_id: int, 
                     original_filename: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Handle file upload securely.
        
        Args:
            file_obj: File-like object from Flask request
            user_id: ID of uploading user
            original_filename: Original filename from client
        
        Returns:
            Tuple of (success, metadata_dict)
        """
        result = {
            'success': False,
            'file_id': None,
            'filename': None,
            'size': 0,
            'mime_type': None,
            'error': None,
            'url': None
        }
        
        # Step 1: Validate filename
        valid, error = FileUploadValidator.validate_filename(original_filename)
        if not valid:
            logger.warning(f"Invalid filename from user {user_id}: {original_filename}")
            result['error'] = error
            return False, result
        
        # Step 2: Read file content
        file_content = file_obj.read()
        file_size = len(file_content)
        
        # Step 3: Validate file size
        valid, error = FileUploadValidator.validate_file_size(file_size)
        if not valid:
            logger.warning(f"Invalid file size from user {user_id}: {file_size}")
            result['error'] = error
            return False, result
        
        # Step 4: Generate safe filename
        file_id = self._generate_file_id(user_id, original_filename)
        _, ext = os.path.splitext(original_filename)
        safe_filename = f"{file_id}{ext}"
        file_path = os.path.join(self.upload_dir, safe_filename)
        
        # Step 5: Save file
        try:
            with open(file_path, 'wb') as f:
                f.write(file_content)
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            result['error'] = "Error saving file"
            return False, result
        
        # Step 6: Validate content
        valid, error = FileUploadValidator.validate_file_content(file_path)
        if not valid:
            os.remove(file_path)
            logger.warning(f"Invalid file content from user {user_id}: {original_filename}")
            result['error'] = error
            return False, result
        
        # Step 7: Scan for threats
        is_safe, threat = FileUploadValidator.scan_for_threats(file_path)
        if not is_safe:
            # Move to quarantine
            quarantine_path = os.path.join(self.quarantine_dir, safe_filename)
            os.rename(file_path, quarantine_path)
            logger.warning(f"File quarantined from user {user_id}: {original_filename} - {threat}")
            result['error'] = threat
            return False, result
        
        # Step 8: Get MIME type
        mime_type, _ = mimetypes.guess_type(original_filename)
        
        # Return success
        result['success'] = True
        result['file_id'] = file_id
        result['filename'] = safe_filename
        result['original_filename'] = original_filename
        result['size'] = file_size
        result['mime_type'] = mime_type
        result['url'] = f"/uploads/{safe_filename}"
        
        logger.info(f"File uploaded successfully: user={user_id}, file={safe_filename}, size={file_size}")
        
        return True, result
    
    @staticmethod
    def _generate_file_id(user_id: int, filename: str) -> str:
        """
        Generate unique file ID.
        
        Args:
            user_id: Uploading user ID
            filename: Original filename
        
        Returns:
            Unique file ID
        """
        timestamp = datetime.now().isoformat()
        combined = f"{user_id}:{filename}:{timestamp}"
        file_hash = hashlib.sha256(combined.encode()).hexdigest()[:16]
        return file_hash
    
    @staticmethod
    def get_upload_url(file_path: str) -> str:
        """Get URL for uploaded file."""
        return f"/uploads/{os.path.basename(file_path)}"
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete uploaded file.
        
        Args:
            file_path: Path to file
        
        Returns:
            Success status
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
