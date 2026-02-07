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
            encryption_key = None
            
            # Try to load from config/environment first
            encryption_key = current_app.config.get(
                'FACIAL_ENCRYPTION_KEY',
                os.environ.get('FACIAL_ENCRYPTION_KEY')
            )
            
            # If not found, try to load from encryption.key file
            if not encryption_key:
                key_file = os.path.join(os.getcwd(), 'encryption.key')
                if os.path.exists(key_file):
                    logger.info(f"Loading encryption key from {key_file}")
                    with open(key_file, 'rb') as f:
                        encryption_key = f.read().strip()
                    logger.info("SUCCESS Encryption key loaded from file")
            
            # If still not found, generate and save
            if not encryption_key:
                logger.warning("No encryption key found, generating new one...")
                encryption_key = Fernet.generate_key()
                key_file = os.path.join(os.getcwd(), 'encryption.key')
                with open(key_file, 'wb') as f:
                    f.write(encryption_key)
                logger.warning(f"Generated and saved new encryption key to {key_file}")
            
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            
            self.cipher_suite = Fernet(encryption_key)
            logger.info("SUCCESS Encryption initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}", exc_info=True)
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
            logger.info(f"[CAPTURE] Processing image data ({len(image_data)} bytes)...")
            Image = _get_pil()
            np = _get_numpy()
            cv2 = _get_cv2()
            
            # Convert bytes to image
            logger.info("[CAPTURE] Opening image...")
            image = Image.open(BytesIO(image_data))
            logger.info(f"[CAPTURE] Image opened: format={image.format}, mode={image.mode}, size={image.size}")
            
            image_array = np.array(image)
            logger.info(f"[CAPTURE] Image converted to array: shape={image_array.shape}, dtype={image_array.dtype}")
            
            # Convert RGB if needed
            if len(image_array.shape) == 2:  # Grayscale
                logger.info("[CAPTURE] Converting grayscale to RGB...")
                image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            elif image_array.shape[2] == 4:  # RGBA
                logger.info("[CAPTURE] Converting RGBA to RGB...")
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            
            # Validate image size
            h, w = image_array.shape[:2]
            logger.info(f"[CAPTURE] Final dimensions: {h}x{w}")
            
            if h < 100 or w < 100:
                logger.error(f"[CAPTURE]  Image too small: {h}x{w} (minimum 100x100)")
                raise FaceEncodingError("Image too small for face detection")
            
            if h > 4000 or w > 4000:
                logger.info(f"[CAPTURE] Image large ({h}x{w}), resizing...")
                # Resize large images for performance
                scale = 4000 / max(h, w)
                new_height = int(h * scale)
                new_width = int(w * scale)
                image_array = cv2.resize(image_array, (new_width, new_height))
                logger.info(f"[CAPTURE] Resized to {new_height}x{new_width}")
            
            logger.info(f"[CAPTURE]  Image processing complete: {image_array.shape}")
            return image_array
        except FaceEncodingError:
            raise
        except Exception as e:
            logger.error(f"[CAPTURE]  Image processing failed: {e}", exc_info=True)
            raise FaceEncodingError(f"Failed to process image: {e}")

    def detect_faces(self, image_array: "np.ndarray") -> List[Tuple]:
        """
        Detect faces in image using face_recognition library.
        Uses HOG (Histogram of Oriented Gradients) model for face detection.
        
        Args:
            image_array: Image as numpy array (RGB)
            
        Returns:
            List of face locations as tuples (top, right, bottom, left)
        """
        try:
            logger.info(f"[DETECT] Starting ML-based face detection...")
            if image_array is None:
                logger.error("[DETECT]  Image array is None!")
                raise FaceEncodingError("Image array is None for detection")
            
            h, w = image_array.shape[:2]
            logger.info(f"[DETECT] Image dimensions: {h}x{w}")
            
            # Use face_recognition library to detect faces
            face_recognition = _get_face_recognition()
            logger.info("[DETECT] Detecting faces with HOG model...")
            face_locations = face_recognition.face_locations(image_array, model='hog')
            
            if not face_locations:
                logger.warning("[DETECT]  No faces detected in image")
                # NO FALLBACK - require real face detection for accurate ML-based verification
                # Return empty list instead of using full image as fallback
                return []
            else:
                logger.info(f"[DETECT]  Found {len(face_locations)} face(s)")
                for i, loc in enumerate(face_locations):
                    logger.info(f"[DETECT] Face {i+1}: {loc}")
            
            return face_locations
            
        except Exception as e:
            logger.error(f"[DETECT]  Face detection error: {e}", exc_info=True)
            raise FaceEncodingError(f"Face detection failed: {e}")

    def encode_face(self, image_array: "np.ndarray", 
                   face_location: Optional[Tuple] = None) -> "np.ndarray":
        """
        Generate face encoding from image using face_recognition library (CNN-based ML model).
        Uses proper deep learning-based face encoding for accurate recognition.
        
        Args:
            image_array: Image as numpy array (RGB)
            face_location: Optional pre-detected face location tuple (top, right, bottom, left)
            
        Returns:
            Face encoding as numpy array (128-dimensional vector from dlib CNN model)
        """
        logger.info(f"[ENCODE] Starting ML-based face encoding...")
        np = _get_numpy()
        face_recognition = _get_face_recognition()
        
        # Validate input
        if image_array is None:
            logger.error("[ENCODE]  Image array is None!")
            raise FaceEncodingError("Image array is None")
        
        logger.info(f"[ENCODE] Image shape: {image_array.shape}, dtype: {image_array.dtype}")
        
        try:
            # Detect face locations using face_recognition library
            logger.info("[ENCODE] Detecting faces in image...")
            face_locations = face_recognition.face_locations(image_array, model='hog')
            
            if not face_locations:
                logger.error("[ENCODE]  No face detected in image!")
                raise FaceEncodingError("No face detected in image")
            
            logger.info(f"[ENCODE]  Found {len(face_locations)} face(s)")
            
            # Use the first face location
            face_location = face_locations[0]
            logger.info(f"[ENCODE] Using face location: {face_location}")
            
            # Generate face encoding using face_recognition CNN model
            logger.info("[ENCODE] Generating 128-dimensional face encoding...")
            face_encodings = face_recognition.face_encodings(image_array, [face_location], num_jitters=1)
            
            if not face_encodings:
                logger.error("[ENCODE]  Failed to generate face encoding!")
                raise FaceEncodingError("Failed to generate face encoding")
            
            encoding = face_encodings[0]
            logger.info(f"[ENCODE]  Encoding generated successfully!")
            logger.info(f"[ENCODE] Encoding shape: {encoding.shape}, dtype: {encoding.dtype}")
            logger.info(f"[ENCODE] Encoding stats: min={encoding.min():.4f}, max={encoding.max():.4f}, mean={encoding.mean():.4f}")
            
            return encoding
            
        except FaceEncodingError:
            raise
        except Exception as e:
            logger.error(f"[ENCODE]  ML-based encoding failed: {e}", exc_info=True)
            raise FaceEncodingError(f"Face encoding failed: {str(e)}")

    def encrypt_encoding(self, encoding: "np.ndarray") -> str:
        """
        Encrypt and encode face encoding for storage
        
        Args:
            encoding: Face encoding array
            
        Returns:
            Encrypted base64-encoded string
        """
        try:
            np = _get_numpy()
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
            logger.info(f"[DECRYPT] Starting decryption of {len(encrypted_b64)} bytes...")
            np = _get_numpy()
            # Decode from base64
            logger.info("[DECRYPT] Decoding base64...")
            encrypted = base64.b64decode(encrypted_b64)
            logger.info(f"[DECRYPT] Base64 decoded: {len(encrypted)} bytes")
            
            # Decrypt
            logger.info("[DECRYPT] Decrypting with Fernet...")
            encoding_bytes = self.cipher_suite.decrypt(encrypted)
            logger.info(f"[DECRYPT] Decrypted: {len(encoding_bytes)} bytes")
            
            # Convert back to numpy array
            logger.info(f"[DECRYPT] Converting to numpy array (dtype=float32)...")
            encoding = np.frombuffer(encoding_bytes, dtype=np.float32)
            logger.info(f"[DECRYPT]  Decryption successful: shape={encoding.shape}")
            
            return encoding
        except Exception as e:
            logger.error(f"[DECRYPT]  Encoding decryption failed: {e}", exc_info=True)
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
            
            logger.info(f"[ENROLL] Starting enrollment for admin {admin_id}, image_size={len(image_data)} bytes, label={image_label}")
            
            # Process image
            logger.info("[ENROLL] Processing image...")
            image_array = self.capture_face_from_image(image_data)
            logger.info(f"[ENROLL] Image processed, shape={image_array.shape}")
            
            # Detect and encode face
            logger.info(f"[ENROLL] Detecting faces in image...")
            face_locations = self.detect_faces(image_array)
            logger.info(f"[ENROLL] Found {len(face_locations)} face location(s)")
            
            if not face_locations:
                logger.error("[ENROLL] No faces detected in image")
                return {
                    'success': False,
                    'message': 'No face detected in image',
                    'enrollment_id': None
                }
            
            logger.info(f"[ENROLL] Encoding first face...")
            face_encoding = self.encode_face(image_array, face_locations[0])
            logger.info(f"[ENROLL] Face encoded successfully, shape={face_encoding.shape}")
            
            # Encrypt encoding
            logger.info("[ENROLL] Encrypting encoding...")
            encrypted_encoding = self.encrypt_encoding(face_encoding)
            logger.info(f"[ENROLL] Encoding encrypted successfully")
            
            # Extract face region for preview
            top, right, bottom, left = face_locations[0]
            face_image = image_array[top:bottom, left:right]
            Image = _get_pil()
            face_image_pil = Image.fromarray(face_image.astype('uint8'))
            
            # Convert to base64 for storage
            buffer = BytesIO()
            face_image_pil.save(buffer, format='JPEG', quality=85)
            face_preview = base64.b64encode(buffer.getvalue()).decode('utf-8')
            logger.info(f"[ENROLL] Face preview generated: {len(face_preview)} bytes")
            
            # Store facial data
            logger.info("[ENROLL] Storing facial data in database...")
            facial_data = FacialIDData(
                admin_id=admin_id,
                facial_encoding=encrypted_encoding,
                face_preview=face_preview,
                encoding_label=image_label,
                encoding_hash=hashlib.sha256(encrypted_encoding.encode()).hexdigest(),
                is_verified=True,  # Auto-verified since captured from camera (not external image)
                enrolled_at=datetime.utcnow(),
                verified_at=None,
                successful_unlocks=0,
                failed_attempts=0,
                last_unlock_at=None,
                last_failed_attempt_at=None
            )
            
            db.session.add(facial_data)
            db.session.commit()
            
            logger.info(f"[ENROLL]  Facial ID enrolled successfully for admin {admin_id}, ID={facial_data.id}")
            
            return {
                'success': True,
                'message': 'Face enrollment successful',
                'admin_id': admin_id,
                'encoding_id': facial_data.id,
                'face_preview': face_preview,
                'status': 'pending_verification'
            }
            
        except FaceEncodingError as e:
            logger.error(f"[ENROLL]  Face encoding error: {e}")
            return {
                'success': False,
                'message': str(e),
                'encoding_id': None
            }
        except Exception as e:
            logger.error(f"[ENROLL]  Facial enrollment error: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"Enrollment failed: {str(e)}",
                'encoding_id': None
            }

    def enroll_admin_face_descriptor(self, admin_id: int, descriptor: list, 
                                    label: str = "Primary Face") -> Tuple[bool, Dict]:
        """
        Enroll admin face using pre-computed face descriptor (from client-side face-api.js)
        
        Args:
            admin_id: Admin user ID
            descriptor: 128-dimensional face descriptor array from face-api.js
            label: Label for this face encoding
            
        Returns:
            Tuple of (success: bool, details: dict)
        """
        try:
            from app import db
            from app.models import FacialIDData
            
            np = _get_numpy()
            
            # Convert descriptor list to numpy array
            descriptor_array = np.array(descriptor, dtype=np.float32)
            
            # Validate descriptor
            if descriptor_array.shape != (128,):
                return False, {'error': 'Invalid descriptor dimensions. Expected 128-dimensional array.'}
            
            # Encrypt descriptor
            encrypted_descriptor = self.encrypt_encoding(descriptor_array)
            
            # Create hash for uniqueness checking
            descriptor_hash = hashlib.sha256(encrypted_descriptor.encode()).hexdigest()
            
            # Check if this exact face is already enrolled
            existing = FacialIDData.query.filter_by(
                admin_id=admin_id,
                encoding_hash=descriptor_hash
            ).first()
            
            if existing:
                return False, {'error': 'This face is already enrolled'}
            
            # Store facial data
            facial_data = FacialIDData(
                admin_id=admin_id,
                facial_encoding=encrypted_descriptor,
                face_preview='',  # No preview for descriptor-based enrollment
                encoding_label=label,
                encoding_hash=descriptor_hash,
                is_verified=True,  # Automatically verified (client-side validated)
                enrolled_at=datetime.utcnow(),
                verified_at=datetime.utcnow(),
                successful_unlocks=0,
                failed_attempts=0,
                last_unlock_at=None,
                last_failed_attempt_at=None,
                device_info='Web Client',
                camera_type='Web API',
                capture_quality=1.0  # High quality since from face-api.js detection
            )
            
            db.session.add(facial_data)
            db.session.commit()
            
            logger.info(f"Facial ID descriptor enrolled for admin {admin_id}")
            return True, {'message': 'Facial ID successfully enrolled', 'face_id': facial_data.id}
            
        except Exception as e:
            logger.error(f"Facial enrollment with descriptor error: {e}")
            return False, {'error': str(e)}

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
            
            logger.info(f"[VERIFY_START] ========== FACIAL VERIFICATION STARTED ==========")
            logger.info(f"[VERIFY_START] Admin ID: {admin_id}")
            logger.info(f"[VERIFY_START] Image data size: {len(image_data)} bytes")
            
            # Get enrolled facial data for admin
            enrolled_faces = FacialIDData.query.filter_by(
                admin_id=admin_id,
                is_verified=True
            ).all()
            
            logger.info(f"[VERIFY_START] Found {len(enrolled_faces)} enrolled verified faces for admin {admin_id}")
            
            if not enrolled_faces:
                logger.warning(f"[VERIFY_START]  No enrolled faces found for admin {admin_id}")
                return False, {
                    'success': False,
                    'message': 'No enrolled faces found for this admin',
                    'confidence': 0.0,
                    'match_count': 0
                }
            
            # Process verification image
            logger.info(f"[VERIFY_PROCESS] Converting image bytes to PIL Image...")
            verification_image = self.capture_face_from_image(image_data)
            logger.info(f"[VERIFY_PROCESS]  Image converted, size: {verification_image.size}")
            
            logger.info(f"[VERIFY_PROCESS] Detecting faces in verification image...")
            verification_locations = self.detect_faces(verification_image)
            logger.info(f"[VERIFY_PROCESS]  Face detection complete: found {len(verification_locations)} face(s)")
            
            if not verification_locations:
                logger.error(f"[VERIFY_PROCESS]  No faces detected in verification image!")
                return False, {
                    'success': False,
                    'message': 'No face detected in image. Please try again.',
                    'confidence': 0.0,
                    'match_count': 0
                }
            
            logger.info(f"[VERIFY_PROCESS] Encoding first detected face...")
            verification_encoding = self.encode_face(
                verification_image, 
                verification_locations[0]
            )
            logger.info(f"[VERIFY_PROCESS]  Face encoding generated: shape={verification_encoding.shape if hasattr(verification_encoding, 'shape') else len(verification_encoding)}")
            
            # Compare against enrolled faces
            matches = []
            match_count = 0
            
            logger.info(f"[VERIFY] Comparing against {len(enrolled_faces)} enrolled face(s)")
            
            for idx, facial_data in enumerate(enrolled_faces, 1):
                try:
                    logger.info(f"[VERIFY] Processing enrolled face {idx}/{len(enrolled_faces)} (ID={facial_data.id}, label={facial_data.encoding_label})...")
                    
                    # Decrypt enrolled encoding
                    enrolled_encoding = self.decrypt_encoding(
                        facial_data.facial_encoding
                    )
                    
                    # Compare encodings using Euclidean distance (face_recognition library standard)
                    np = _get_numpy()
                    distance = np.linalg.norm(enrolled_encoding - verification_encoding)
                    
                    # SECURITY FIX: Use stricter tolerance for biometric authentication
                    # Default 0.6 was too lenient and allowed false positives
                    # New strict tolerance 0.4 requires much closer face match
                    # Lower tolerance = stricter (more secure)
                    # 0.4 = highly secure for biometric authentication
                    # This rejects unknown/different faces more reliably
                    tolerance = 0.4  # STRICT TOLERANCE - was 0.6 (too lenient)
                    is_match = distance <= tolerance
                    
                    # Convert distance to confidence percentage
                    # distance 0.0 = perfect match (100% confidence)
                    # distance 0.4 = borderline match (0% confidence)
                    # distance > 0.4 = no match (0% confidence)
                    confidence = max(0.0, 1.0 - (distance / tolerance))
                    
                    matches.append({
                        'encoding_id': facial_data.id,
                        'label': facial_data.encoding_label,
                        'distance': float(distance),
                        'confidence': float(confidence),
                        'is_match': is_match
                    })
                    
                    logger.info(f"[VERIFY]  Face {idx} comparison: distance={distance:.4f}, confidence={confidence:.2%}, match={is_match}, tolerance={tolerance}")
                    
                    if is_match:
                        match_count += 1
                        logger.info(f"[VERIFY]  MATCH found! ({match_count} match(es) so far)")
                        
                except Exception as e:
                    logger.error(f"[VERIFY]  Error comparing encoding {idx} (ID={facial_data.id}): {e}", exc_info=True)
                    continue

            
            # Require at least one match with MINIMUM confidence threshold
            # confidence < 50% = not confident enough, reject
            # confidence >= 50% = reasonably confident match
            minimum_confidence = 0.5  # 50% confidence minimum required
            
            # Only count matches that meet confidence threshold
            valid_matches = [m for m in matches if m['confidence'] >= minimum_confidence]
            match_count = len(valid_matches)
            
            # Must have at least one valid match to proceed
            is_verified = match_count > 0
            best_match = max(valid_matches, key=lambda x: x['confidence']) if valid_matches else None
            
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

    def verify_admin_face_descriptor(self, admin_id: int, descriptor_array: List) -> Tuple[bool, Dict]:
        """
        Verify admin identity using face descriptor directly (from client-side face-api.js)
        
        Args:
            admin_id: Admin user ID
            descriptor_array: Face descriptor as list of floats (128-dimensional from face-api.js)
            
        Returns:
            Tuple of (is_verified: bool, details: dict)
        """
        try:
            from app.models import FacialIDData
            import json
            numpy = _get_numpy()
            
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
            
            # Convert descriptor array to numpy array
            verification_descriptor = numpy.array(descriptor_array, dtype=numpy.float32)
            
            # Compare against enrolled face descriptors
            matches = []
            match_count = 0
            
            for facial_data in enrolled_faces:
                try:
                    # Get stored descriptor (should be JSON)
                    if facial_data.face_descriptor:
                        stored_descriptor = json.loads(facial_data.face_descriptor)
                        stored_descriptor = numpy.array(stored_descriptor, dtype=numpy.float32)
                        
                        # Calculate Euclidean distance between descriptors
                        distance = numpy.linalg.norm(verification_descriptor - stored_descriptor)
                        
                        # Face-api.js uses 0.5 as threshold for high confidence
                        is_match = distance <= 0.5
                        confidence = max(0.0, 1.0 - (distance / 2.0))  # Convert distance to confidence
                        
                        matches.append({
                            'encoding_id': facial_data.id,
                            'label': facial_data.encoding_label,
                            'distance': float(distance),
                            'confidence': float(min(1.0, confidence)),
                            'is_match': is_match
                        })
                        
                        if is_match:
                            match_count += 1
                            
                except Exception as e:
                    logger.error(f"Error comparing descriptor for facial data {facial_data.id}: {e}")
                    continue
            
            # Require at least one match
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
                
                logger.info(f"Facial verification successful (descriptor) for admin {admin_id}")
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
                
                logger.warning(f"Facial verification failed (descriptor) for admin {admin_id}")
            
            return is_verified, {
                'success': is_verified,
                'message': 'Facial verification successful' if is_verified 
                          else 'Face not recognized',
                'confidence': float(best_match['confidence']) if best_match else 0.0,
                'match_count': match_count,
                'total_attempts': len(enrolled_faces),
                'matches': matches
            }
            
        except Exception as e:
            logger.error(f"Facial descriptor verification error: {e}")
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
            
            logger.info(f"Getting facial stats for admin {admin_id}")
            facial_data = FacialIDData.query.filter_by(admin_id=admin_id).all()
            logger.info(f"Found {len(facial_data)} facial records for admin {admin_id}")
            
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
            
            result = {
                'enrolled': True,
                'enrollment_count': len(facial_data),
                'verified_count': verified_count,
                'total_unlocks': total_unlocks,
                'total_failed': total_failed,
                'enrolled_at': facial_data[0].enrolled_at.isoformat() if facial_data and facial_data[0].enrolled_at else None,
                'last_unlock': max((f.last_unlock_at for f in facial_data if f.last_unlock_at), 
                                  default=None),
                'last_failed': max((f.last_failed_attempt_at for f in facial_data if f.last_failed_attempt_at), 
                                  default=None)
            }
            
            # Convert datetime objects to isoformat if they exist
            if result['last_unlock']:
                result['last_unlock'] = result['last_unlock'].isoformat()
            if result['last_failed']:
                result['last_failed'] = result['last_failed'].isoformat()
            
            logger.info(f"Facial stats: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to get facial stats: {e}", exc_info=True)
            return {'enrolled': False, 'error': str(e)}

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
