"""
Database Encryption using OpenSSL
Encrypts sensitive data fields with AES-256-GCM
"""

import os
import base64
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
from flask import current_app

logger = logging.getLogger(__name__)

class DatabaseEncryption:
    """Encrypt/decrypt sensitive data for database storage"""
    
    ALGORITHM = 'AES-256-GCM'
    KEY_SIZE = 32  # 256 bits
    IV_SIZE = 12   # 96 bits for GCM
    TAG_SIZE = 16  # 128 bits
    SALT_SIZE = 16  # 128 bits
    
    def __init__(self, master_key=None):
        """Initialize with master encryption key"""
        if master_key is None:
            master_key = os.environ.get('DB_ENCRYPTION_KEY')
        
        if not master_key:
            raise ValueError("DB_ENCRYPTION_KEY environment variable not set")
        
        # Decode base64 key if it's a string
        if isinstance(master_key, str):
            try:
                self.master_key = base64.b64decode(master_key)
            except Exception:
                self.master_key = master_key.encode('utf-8')
        else:
            self.master_key = master_key
        
        # Validate key size
        if len(self.master_key) != self.KEY_SIZE:
            raise ValueError(f"Invalid key size. Expected {self.KEY_SIZE} bytes, got {len(self.master_key)}")
    
    @staticmethod
    def generate_key():
        """Generate a new encryption key"""
        return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
    
    def derive_key(self, password, salt=None):
        """Derive encryption key from password using PBKDF2"""
        if salt is None:
            salt = secrets.token_bytes(self.SALT_SIZE)
        elif isinstance(salt, str):
            salt = base64.b64decode(salt)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=100000
        )
        
        key = kdf.derive(password.encode('utf-8') if isinstance(password, str) else password)
        return key, base64.b64encode(salt).decode('utf-8')
    
    def encrypt(self, plaintext, key=None):
        """Encrypt plaintext with AES-256-GCM"""
        if key is None:
            key = self.master_key
        elif isinstance(key, str):
            key = base64.b64decode(key)
        
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # Generate random IV and get key
        iv = secrets.token_bytes(self.IV_SIZE)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        # Get authentication tag
        tag = encryptor.tag
        
        # Combine IV + ciphertext + tag
        encrypted_data = iv + ciphertext + tag
        
        # Return base64 encoded
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data, key=None):
        """Decrypt ciphertext with AES-256-GCM"""
        if key is None:
            key = self.master_key
        elif isinstance(key, str):
            key = base64.b64decode(key)
        
        if isinstance(encrypted_data, str):
            encrypted_data = base64.b64decode(encrypted_data)
        
        # Extract IV, ciphertext, and tag
        iv = encrypted_data[:self.IV_SIZE]
        ciphertext = encrypted_data[self.IV_SIZE:-self.TAG_SIZE]
        tag = encrypted_data[-self.TAG_SIZE:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext.decode('utf-8')

class EncryptedField:
    """SQLAlchemy type for encrypted fields"""
    
    def __init__(self, underlying_type):
        self.underlying_type = underlying_type
    
    def process_bind_param(self, value, dialect):
        """Encrypt on write"""
        if value is None:
            return None
        
        try:
            enc = get_db_encryption()
            return enc.encrypt(value)
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return value
    
    def process_result_value(self, value, dialect):
        """Decrypt on read"""
        if value is None:
            return None
        
        try:
            enc = get_db_encryption()
            return enc.decrypt(value)
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return value

class FieldEncryption:
    """Decorator for model-level field encryption"""
    
    def __init__(self, *fields):
        self.fields = fields
    
    def __call__(self, cls):
        """Apply encryption to specified fields"""
        for field_name in self.fields:
            if hasattr(cls, field_name):
                # Mark field for encryption
                setattr(cls, f'_encrypt_{field_name}', True)
        
        return cls

def get_db_encryption():
    """Get database encryption instance from app context"""
    from flask import current_app
    
    if 'db_encryption' not in current_app.config:
        current_app.config['db_encryption'] = DatabaseEncryption()
    
    return current_app.config['db_encryption']
