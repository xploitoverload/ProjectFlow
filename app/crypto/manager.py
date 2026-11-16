"""
Cryptographic Provider Manager for ProjectFlow.
Provides unified, pluggable password hashing and database field encryption.
Supports zero-friction transparent algorithm migration and dynamic user-supplied plugins.
"""

import os
import importlib
import logging
from typing import Dict, Optional, Tuple, Type
from app.crypto.base import BasePasswordHasher, BaseFieldCipher
from app.crypto.hasher_providers import (
    Argon2idHasher,
    PBKDF2SHA512Hasher,
    ScryptHasher,
    BcryptHasher,
    CustomHasherProvider
)
from app.crypto.cipher_providers import (
    AES256GCMCipher,
    ChaCha20Poly1305Cipher,
    FernetCipher,
    CustomCipherProvider
)

logger = logging.getLogger(__name__)


def _load_class_from_string(path: str):
    """Dynamically import and return a class from a dotted path (e.g. module.submodule:ClassName)."""
    if ':' in path:
        module_path, class_name = path.split(':', 1)
    elif '.' in path:
        module_path, class_name = path.rsplit('.', 1)
    else:
        raise ValueError(f"Invalid class import path: {path}")
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class CryptoManager:
    """
    Central cryptographic registry and orchestration engine.
    """

    def __init__(self):
        self._hashers: Dict[str, BasePasswordHasher] = {}
        self._ciphers: Dict[str, BaseFieldCipher] = {}
        self._default_hasher_name: str = "argon2id"
        self._default_cipher_name: str = "aes_256_gcm"
        self._master_key: Optional[bytes] = None

        # Register standard default providers
        self.register_hasher("argon2id", Argon2idHasher())
        self.register_hasher("pbkdf2_sha512", PBKDF2SHA512Hasher())
        self.register_hasher("scrypt", ScryptHasher())
        self.register_hasher("bcrypt", BcryptHasher())

        self.register_cipher("aes_256_gcm", AES256GCMCipher())
        self.register_cipher("chacha20_poly1305", ChaCha20Poly1305Cipher())
        self.register_cipher("fernet", FernetCipher())

        # Load environment preferences if available
        self._init_from_env()

    def _init_from_env(self):
        env_hasher = os.environ.get("CRYPTO_PASSWORD_HASHER")
        if env_hasher:
            self.set_default_hasher(env_hasher)

        env_cipher = os.environ.get("CRYPTO_FIELD_CIPHER")
        if env_cipher:
            self.set_default_cipher(env_cipher)

    def set_master_key(self, key: bytes):
        """Set fallback encryption master key for cipher operations."""
        self._master_key = key

    def get_master_key(self) -> bytes:
        if self._master_key:
            return self._master_key
        # Check environment
        env_key = os.environ.get("SECRET_ENCRYPTION_KEY") or os.environ.get("DB_ENCRYPTION_KEY")
        if env_key:
            return env_key.encode("utf-8") if isinstance(env_key, str) else env_key
        # Fallback key for development
        return b"SSPcxXLWjHXEAw4EvOOkBQ9bxocTd8m1O-0VaHe8bRc="

    # =========================================================================
    # Hasher Management
    # =========================================================================

    def register_hasher(self, name: str, hasher: BasePasswordHasher):
        """Register a new or custom password hashing provider."""
        self._hashers[name] = hasher
        logger.info(f"Registered cryptographic password hasher: '{name}' ({hasher.__class__.__name__})")

    def set_default_hasher(self, name_or_class_path: str):
        """Set the active default password hashing algorithm."""
        if ":" in name_or_class_path or ("." in name_or_class_path and not name_or_class_path in self._hashers):
            try:
                cls = _load_class_from_string(name_or_class_path)
                instance = cls()
                name = getattr(instance, "name", name_or_class_path)
                self.register_hasher(name, instance)
                self._default_hasher_name = name
                return
            except Exception as e:
                logger.error(f"Failed to load custom hasher class from '{name_or_class_path}': {e}")
                raise

        if name_or_class_path in self._hashers:
            self._default_hasher_name = name_or_class_path
        else:
            raise ValueError(f"Unknown password hasher '{name_or_class_path}'. Available: {list(self._hashers.keys())}")

    def get_default_hasher(self) -> BasePasswordHasher:
        return self._hashers[self._default_hasher_name]

    def hash_password(self, password: str, algorithm: Optional[str] = None) -> str:
        """Hash plaintext password using the specified or active algorithm."""
        hasher = self._hashers.get(algorithm) if algorithm else self.get_default_hasher()
        if not hasher:
            raise ValueError(f"Password hasher '{algorithm}' not registered")
        return hasher.hash(password)

    def verify_password(self, stored_hash: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Verify password against stored hash.
        Supports multi-algorithm verification and automatic rehashing/migration.
        
        Returns:
            (is_valid: bool, new_hash_if_rehash_needed: Optional[str])
        """
        if not stored_hash or not password:
            return False, None

        matched_hasher = None

        # 1. Find hasher that recognizes the stored hash format
        for name, hasher in self._hashers.items():
            if hasher.can_handle(stored_hash):
                matched_hasher = hasher
                break

        # 2. Fallback check for Werkzeug / legacy formats
        if not matched_hasher and stored_hash.startswith("pbkdf2:"):
            matched_hasher = self._hashers.get("pbkdf2_sha512")

        if not matched_hasher:
            # Check default hasher as last resort
            matched_hasher = self.get_default_hasher()

        is_valid = matched_hasher.verify(password, stored_hash)

        if not is_valid:
            return False, None

        # 3. Check if password needs to be rehashed into the currently active default algorithm
        active_hasher = self.get_default_hasher()
        rehash_needed = False

        if matched_hasher != active_hasher:
            rehash_needed = True
        elif active_hasher.needs_rehash(stored_hash):
            rehash_needed = True

        new_hash = active_hasher.hash(password) if rehash_needed else None
        return True, new_hash

    # =========================================================================
    # Cipher Management
    # =========================================================================

    def register_cipher(self, name: str, cipher: BaseFieldCipher):
        """Register a new or custom authenticated field cipher."""
        self._ciphers[name] = cipher
        logger.info(f"Registered cryptographic field cipher: '{name}' ({cipher.__class__.__name__})")

    def set_default_cipher(self, name_or_class_path: str):
        """Set active default field cipher."""
        if ":" in name_or_class_path or ("." in name_or_class_path and not name_or_class_path in self._ciphers):
            try:
                cls = _load_class_from_string(name_or_class_path)
                instance = cls()
                name = getattr(instance, "name", name_or_class_path)
                self.register_cipher(name, instance)
                self._default_cipher_name = name
                return
            except Exception as e:
                logger.error(f"Failed to load custom cipher class from '{name_or_class_path}': {e}")
                raise

        if name_or_class_path in self._ciphers:
            self._default_cipher_name = name_or_class_path
        else:
            raise ValueError(f"Unknown field cipher '{name_or_class_path}'. Available: {list(self._ciphers.keys())}")

    def get_default_cipher(self) -> BaseFieldCipher:
        return self._ciphers[self._default_cipher_name]

    def encrypt(
        self,
        plaintext: Optional[str],
        key: Optional[bytes] = None,
        cipher_name: Optional[str] = None,
        associated_data: Optional[bytes] = None
    ) -> Optional[str]:
        """Encrypt plaintext using the active or specified authenticated cipher."""
        if plaintext is None:
            return None
        cipher = self._ciphers.get(cipher_name) if cipher_name else self.get_default_cipher()
        if not cipher:
            raise ValueError(f"Cipher '{cipher_name}' not registered")
        k = key or self.get_master_key()
        return cipher.encrypt(plaintext, k, associated_data)

    def decrypt(
        self,
        ciphertext: Optional[str],
        key: Optional[bytes] = None,
        associated_data: Optional[bytes] = None
    ) -> Optional[str]:
        """
        Decrypt ciphertext using the matching cipher (supports auto-detection across all ciphers).
        """
        if ciphertext is None:
            return None

        k = key or self.get_master_key()

        # Find cipher that can handle this format
        for name, cipher in self._ciphers.items():
            if cipher.can_handle(ciphertext):
                try:
                    return cipher.decrypt(ciphertext, k, associated_data)
                except Exception as e:
                    logger.debug(f"Cipher {name} failed decryption: {e}")

        # Fallback to default cipher
        try:
            return self.get_default_cipher().decrypt(ciphertext, k, associated_data)
        except Exception:
            return None


# Global singleton instance
crypto_manager = CryptoManager()
