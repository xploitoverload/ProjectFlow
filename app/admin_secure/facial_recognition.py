"""
Facial Recognition System for Admin Authentication
Enhanced security layer for admin access with biometric verification
"""

import os
import base64
import hashlib
import logging
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional, Tuple, List, Dict, TYPE_CHECKING

from flask import current_app
from sqlalchemy import and_, desc
from cryptography.fernet import Fernet

# For type hints only - these won't be imported at module load time
if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

# Lazy imports for heavy dependencies
def _get_face_recognition():
    """Lazy import face_recognition to avoid slow startup"""
    global _face_recognition_module
    if '_face_recognition_module' not in globals():
        import face_recognition
        _face_recognition_module = face_recognition
    return _face_recognition_module

def _get_cv2():
    """Lazy import cv2 to avoid slow startup"""
    global _cv2_module
    if '_cv2_module' not in globals():
        import cv2
        _cv2_module = cv2
    return _cv2_module

def _get_numpy():
    """Lazy import numpy to avoid slow startup"""
    global _numpy_module
    if '_numpy_module' not in globals():
        import numpy as np
        _numpy_module = np
    return _numpy_module

def _get_pil():
    """Lazy import PIL to avoid slow startup"""
    global _pil_module
    if '_pil_module' not in globals():
        from PIL import Image
        _pil_module = Image
    return _pil_module


class FacialRecognitionError(Exception):
    """Raised when facial recognition operation fails"""
    pass


class FaceEncodingError(FacialRecognitionError):
    """Raised when face encoding fails"""
    pass


class FaceVerificationError(FacialRecognitionError):
    """Raised when face verification fails"""
    pass


class FacialIDManager:
    """
    Manages facial recognition enrollment, verification, and storage
    Provides biometric authentication layer for admin access
    """

    def __init__(self):
        """Initialize facial recognition manager"""
        self.tolerance = 0.6  # Face matching tolerance (0.6 is moderate security)
        self.model = "hog"  # Use HOG for speed, can use "cnn" for accuracy
        self.cipher_suite = None
        self._init_encryption()

    def _init_encryption(self):
        """Initialize encryption for facial data storage"""
        try:
            encryption_key = current_app.config.get(
                'FACIAL_ENCRYPTION_KEY',
                os.environ.get('FACIAL_ENCRYPTION_KEY')
            )
            
            if not encryption_key:
                # Generate a key if not provided
                encryption_key = Fernet.generate_key()
                logger.warning("Generated new facial encryption key - store this securely!")
            
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            
            self.cipher_suite = Fernet(encryption_key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise FacialRecognitionError(f"Encryption initialization failed: {e}")

    def capture_face_from_image(self, image_data: bytes) -> "Optional":
        """
        Capture and extract face from image data
        
        Args:
            image_data: Raw image bytes (JPEG, PNG)
            
        Returns:
            Image array if face found, None otherwise
            
        Raises:
            FaceEncodingError: If image processing fails
        """
        try:
            # Lazy import heavy dependencies
            Image = _get_pil()
            np = _get_numpy()
            cv2 = _get_cv2()
            
            # Convert bytes to image
            image = Image.open(BytesIO(image_data))
            image_array = np.array(image)
            
            # Convert RGB if needed
            if len(image_array.shape) == 2:  # Grayscale
                image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            elif image_array.shape[2] == 4:  # RGBA
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            
            # Validate image size
            if image_array.shape[0] < 100 or image_array.shape[1] < 100:
                raise FaceEncodingError("Image too small for face detection")
            
            if image_array.shape[0] > 4000 or image_array.shape[1] > 4000:
                # Resize large images for performance
                scale = 4000 / max(image_array.shape[0], image_array.shape[1])
                new_height = int(image_array.shape[0] * scale)
                new_width = int(image_array.shape[1] * scale)
                image_array = cv2.resize(image_array, (new_width, new_height))
            
            return image_array
        except FaceEncodingError:
            raise
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise FaceEncodingError(f"Failed to process image: {e}")

    def detect_faces(self, image_array: "np.ndarray") -> List[Tuple]:
        """
        Detect face locations in image
        
        Args:
            image_array: Image as numpy array
            
        Returns:
            List of face locations (top, right, bottom, left)
        """
        try:
            # Find faces in image
            face_locations = face_recognition.face_locations(
                image_array,
                model=self.model
            )
            
            if not face_locations:
                raise FaceEncodingError("No face detected in image")
            
            if len(face_locations) > 1:
                logger.warning(f"Multiple faces detected ({len(face_locations)}), using largest")
                # Use the largest face (most centered/clear)
                face_locations = [max(face_locations, 
                    key=lambda f: (f[2]-f[0]) * (f[1]-f[3]))]
            
            return face_locations
        except FaceEncodingError:
            raise
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            raise FaceEncodingError(f"Face detection failed: {e}")

    def encode_face(self, image_array: "np.ndarray", 
                   face_location: Optional[Tuple] = None) -> "np.ndarray":
        """
        Generate face encoding from image
        
        Args:
            image_array: Image as numpy array
            face_location: Optional pre-detected face location
            
        Returns:
            Face encoding as numpy array (128-dimensional vector)
            
        Raises:
            FaceEncodingError: If encoding fails
        """
        try:
            # Detect face if not provided
            if face_location is None:
                face_locations = self.detect_faces(image_array)
                face_location = face_locations[0]
            
            # Generate face encoding
            face_encodings = face_recognition.face_encodings(
                image_array,
                [face_location],
                model="small"  # Use the default encoding model
            )
            
            if not face_encodings:
                raise FaceEncodingError("Failed to generate face encoding")
            
            return face_encodings[0]
        except FaceEncodingError:
            raise
        except Exception as e:
            logger.error(f"Encoding generation failed: {e}")
            raise FaceEncodingError(f"Could not encode face: {e}")

    def encrypt_encoding(self, encoding: "np.ndarray") -> str:
        """
        Encrypt and encode face encoding for storage
        
        Args:
            encoding: Face encoding array
            
        Returns:
            Encrypted base64-encoded string
        """
        try:
            # Convert numpy array to bytes
            encoding_bytes = encoding.astype(np.float32).tobytes()
            
            # Encrypt
            encrypted = self.cipher_suite.encrypt(encoding_bytes)
            
            # Encode to base64 for storage
            encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
            
            return encrypted_b64
        except Exception as e:
            logger.error(f"Encoding encryption failed: {e}")
            raise FacialRecognitionError(f"Failed to encrypt encoding: {e}")

    def decrypt_encoding(self, encrypted_b64: str) -> "np.ndarray":
        """
        Decrypt and decode face encoding from storage
        
        Args:
            encrypted_b64: Encrypted base64-encoded string
            
        Returns:
            Face encoding array
        """
        try:
            # Decode from base64
            encrypted = base64.b64decode(encrypted_b64)
            
            # Decrypt
            encoding_bytes = self.cipher_suite.decrypt(encrypted)
            
            # Convert back to numpy array
            encoding = np.frombuffer(encoding_bytes, dtype=np.float32)
            
            return encoding
        except Exception as e:
            logger.error(f"Encoding decryption failed: {e}")
            raise FacialRecognitionError(f"Failed to decrypt encoding: {e}")

    def enroll_admin_face(self, admin_id: int, image_data: bytes, 
                         image_label: str = "default") -> Dict:
        """
        Enroll admin face for facial recognition
        
        Args:
            admin_id: Admin user ID
            image_data: Image bytes (photo of admin's face)
            image_label: Label for this face encoding (e.g., "phone", "laptop")
            
        Returns:
            Dict with enrollment status and details
            
        Raises:
            FaceEncodingError: If face enrollment fails
        """
        try:
            # Import here to avoid circular imports
            from app import db
            from app.models import FacialIDData
            
            # Process image
            image_array = self.capture_face_from_image(image_data)
            
            # Detect and encode face
            face_locations = self.detect_faces(image_array)
            face_encoding = self.encode_face(image_array, face_locations[0])
            
            # Encrypt encoding
            encrypted_encoding = self.encrypt_encoding(face_encoding)
            
            # Extract face region for preview
            top, right, bottom, left = face_locations[0]
            face_image = image_array[top:bottom, left:right]
            face_image_pil = Image.fromarray(face_image.astype('uint8'))
            
            # Convert to base64 for storage
            buffer = BytesIO()
            face_image_pil.save(buffer, format='JPEG', quality=85)
            face_preview = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Store facial data
            facial_data = FacialIDData(
                admin_id=admin_id,
                facial_encoding=encrypted_encoding,
                face_preview=face_preview,
                encoding_label=image_label,
                encoding_hash=hashlib.sha256(encrypted_encoding.encode()).hexdigest(),
                is_verified=False,  # Require verification after enrollment
                enrolled_at=datetime.utcnow(),
                verified_at=None,
                successful_unlocks=0,
                failed_attempts=0,
                last_unlock_at=None,
                last_failed_attempt_at=None
            )
            
            db.session.add(facial_data)
            db.session.commit()
            
            logger.info(f"Facial ID enrolled for admin {admin_id}")
            
            return {
                'success': True,
                'message': 'Face enrollment successful',
                'admin_id': admin_id,
                'encoding_id': facial_data.id,
                'face_preview': face_preview,
                'status': 'pending_verification'
            }
            
        except FaceEncodingError as e:
            logger.error(f"Face enrollment failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Facial enrollment error: {e}")
            raise FacialRecognitionError(f"Enrollment failed: {e}")

    def verify_admin_face(self, admin_id: int, image_data: bytes) -> Tuple[bool, Dict]:
        """
        Verify admin identity using facial recognition
        
        Args:
            admin_id: Admin user ID
            image_data: Image bytes (captured face to verify)
            
        Returns:
            Tuple of (is_verified: bool, details: dict)
        """
        try:
            # Import here to avoid circular imports
            from app.models import FacialIDData
            
            # Get enrolled facial data for admin
            enrolled_faces = FacialIDData.query.filter_by(
                admin_id=admin_id,
                is_verified=True
            ).all()
            
            if not enrolled_faces:
                return False, {
                    'success': False,
                    'message': 'No enrolled faces found for this admin',
                    'confidence': 0.0,
                    'match_count': 0
                }
            
            # Process verification image
            verification_image = self.capture_face_from_image(image_data)
            verification_locations = self.detect_faces(verification_image)
            verification_encoding = self.encode_face(
                verification_image, 
                verification_locations[0]
            )
            
            # Compare against enrolled faces
            matches = []
            match_count = 0
            
            for facial_data in enrolled_faces:
                try:
                    # Decrypt enrolled encoding
                    enrolled_encoding = self.decrypt_encoding(
                        facial_data.facial_encoding
                    )
                    
                    # Compare encodings
                    distance = face_recognition.face_distance(
                        [enrolled_encoding],
                        verification_encoding
                    )[0]
                    
                    is_match = distance <= self.tolerance
                    confidence = 1.0 - distance  # Convert distance to confidence
                    
                    matches.append({
                        'encoding_id': facial_data.id,
                        'label': facial_data.encoding_label,
                        'distance': float(distance),
                        'confidence': float(confidence),
                        'is_match': is_match
                    })
                    
                    if is_match:
                        match_count += 1
                        
                except Exception as e:
                    logger.error(f"Error comparing encoding {facial_data.id}: {e}")
                    continue
            
            # Require at least one match (can require multiple for higher security)
            is_verified = match_count > 0
            best_match = max(matches, key=lambda x: x['confidence']) if matches else None
            
            if is_verified:
                # Update successful unlock
                best_match_data = FacialIDData.query.get(best_match['encoding_id'])
                if best_match_data:
                    best_match_data.successful_unlocks += 1
                    best_match_data.last_unlock_at = datetime.utcnow()
                    best_match_data.failed_attempts = 0  # Reset failed counter
                    from app import db
                    db.session.commit()
                
                logger.info(f"Facial verification successful for admin {admin_id}")
            else:
                # Update failed attempt
                for facial_data in enrolled_faces:
                    facial_data.failed_attempts += 1
                    facial_data.last_failed_attempt_at = datetime.utcnow()
                    
                    # Lock if too many failed attempts
                    if facial_data.failed_attempts >= 5:
                        facial_data.is_verified = False
                        logger.warning(
                            f"Facial ID locked for admin {admin_id} "
                            f"due to {facial_data.failed_attempts} failed attempts"
                        )
                
                from app import db
                db.session.commit()
                
                logger.warning(f"Facial verification failed for admin {admin_id}")
            
            return is_verified, {
                'success': is_verified,
                'message': 'Facial verification successful' if is_verified 
                          else 'Face not recognized',
                'confidence': float(best_match['confidence']) if best_match else 0.0,
                'match_count': match_count,
                'total_attempts': len(enrolled_faces),
                'matches': matches
            }
            
        except FaceEncodingError as e:
            logger.error(f"Face verification failed: {e}")
            return False, {
                'success': False,
                'message': f'Verification error: {str(e)}',
                'confidence': 0.0,
                'match_count': 0
            }
        except Exception as e:
            logger.error(f"Facial verification error: {e}")
            return False, {
                'success': False,
                'message': 'An error occurred during verification',
                'confidence': 0.0,
                'match_count': 0
            }

    def delete_facial_data(self, admin_id: int) -> bool:
        """
        Delete all facial data for an admin
        
        Args:
            admin_id: Admin user ID
            
        Returns:
            True if deletion successful
        """
        try:
            from app import db
            from app.models import FacialIDData
            
            deleted = FacialIDData.query.filter_by(admin_id=admin_id).delete()
            db.session.commit()
            
            logger.info(f"Deleted {deleted} facial ID records for admin {admin_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete facial data: {e}")
            return False

    def get_admin_facial_stats(self, admin_id: int) -> Dict:
        """
        Get facial ID statistics for admin
        
        Args:
            admin_id: Admin user ID
            
        Returns:
            Dict with enrollment stats and security metrics
        """
        try:
            from app.models import FacialIDData
            
            facial_data = FacialIDData.query.filter_by(admin_id=admin_id).all()
            
            if not facial_data:
                return {
                    'enrolled': False,
                    'enrollment_count': 0,
                    'verified_count': 0,
                    'total_unlocks': 0,
                    'total_failed': 0
                }
            
            verified_count = sum(1 for f in facial_data if f.is_verified)
            total_unlocks = sum(f.successful_unlocks for f in facial_data)
            total_failed = sum(f.failed_attempts for f in facial_data)
            
            return {
                'enrolled': True,
                'enrollment_count': len(facial_data),
                'verified_count': verified_count,
                'total_unlocks': total_unlocks,
                'total_failed': total_failed,
                'enrolled_at': facial_data[0].enrolled_at.isoformat() if facial_data else None,
                'last_unlock': max((f.last_unlock_at for f in facial_data if f.last_unlock_at), 
                                  default=None).isoformat() if any(f.last_unlock_at for f in facial_data) else None,
                'last_failed': max((f.last_failed_attempt_at for f in facial_data if f.last_failed_attempt_at), 
                                  default=None).isoformat() if any(f.last_failed_attempt_at for f in facial_data) else None
            }
        except Exception as e:
            logger.error(f"Failed to get facial stats: {e}")
            return {'error': str(e)}

    def cleanup_old_attempts(self, days: int = 90) -> int:
        """
        Clean up old failed attempt records (privacy/storage management)
        
        Args:
            days: Delete failed attempts older than this many days
            
        Returns:
            Number of records cleaned
        """
        try:
            from app import db
            from app.models import FacialIDData
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Reset failed attempts for old records
            records = FacialIDData.query.filter(
                FacialIDData.last_failed_attempt_at < cutoff_date
            ).all()
            
            for record in records:
                record.failed_attempts = 0
                record.last_failed_attempt_at = None
            
            db.session.commit()
            logger.info(f"Cleaned {len(records)} facial ID records")
            
            return len(records)
        except Exception as e:
            logger.error(f"Failed to cleanup facial attempts: {e}")
            return 0


# Create global instance (lazy loaded)
_facial_id_manager_instance = None

def get_facial_id_manager():
    """Get or create the facial ID manager instance (lazy loading)"""
    global _facial_id_manager_instance
    if _facial_id_manager_instance is None:
        _facial_id_manager_instance = FacialIDManager()
    return _facial_id_manager_instance

# For backwards compatibility - create lazy-loaded proxy
class _FacialIDManagerProxy:
    """Proxy that lazy-loads the FacialIDManager"""
    def __getattr__(self, name):
        return getattr(get_facial_id_manager(), name)

facial_id_manager = _FacialIDManagerProxy()


def require_facial_id(f):
    """
    Decorator to require facial ID verification for admin routes
    Used in addition to 2FA for enhanced security
    """
    from functools import wraps
    from flask import session, jsonify, request
    from flask_login import current_user
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if facial ID is required for this admin
        if not current_app.config.get('FACIAL_ID_REQUIRED_FOR_ADMIN', False):
            return f(*args, **kwargs)
        
        # Check if user is authenticated as admin
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Check if facial ID has been verified in this session
        facial_verified = session.get('facial_id_verified')
        if not facial_verified:
            return jsonify({'error': 'Facial ID verification required'}), 403
        
        # Check verification is still fresh (within 30 minutes)
        facial_verified_at = session.get('facial_id_verified_at')
        if facial_verified_at:
            verified_time = datetime.fromisoformat(facial_verified_at)
            if (datetime.utcnow() - verified_time).total_seconds() > 1800:  # 30 minutes
                session.pop('facial_id_verified', None)
                session.pop('facial_id_verified_at', None)
                return jsonify({'error': 'Facial ID verification expired'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
