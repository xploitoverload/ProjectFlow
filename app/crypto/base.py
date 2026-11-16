"""
Abstract Base Classes for Pluggable Cryptographic Providers.
Allows deployers to configure or implement custom hashing algorithms (Argon2id, PBKDF2, Scrypt, Bcrypt, HSM/Custom)
and authenticated field encryption ciphers (AES-256-GCM, ChaCha20-Poly1305, Fernet, Post-Quantum).
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple


class BasePasswordHasher(ABC):
    """Abstract base class for password hashing providers."""

    name: str = "base"

    @abstractmethod
    def hash(self, password: str) -> str:
        """
        Hash plaintext password and return self-describing hash string.
        """
        pass

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """
        Verify plaintext password against stored hash.
        Must use constant-time comparison.
        """
        pass

    @abstractmethod
    def needs_rehash(self, hashed: str) -> bool:
        """
        Check if stored hash needs to be recomputed (e.g. outdated parameters).
        """
        pass

    @abstractmethod
    def can_handle(self, hashed: str) -> bool:
        """
        Return True if this provider can parse and verify this hash format.
        """
        pass


class BaseFieldCipher(ABC):
    """Abstract base class for authenticated field encryption providers."""

    name: str = "base"

    @abstractmethod
    def encrypt(self, plaintext: str, key: bytes, associated_data: Optional[bytes] = None) -> str:
        """
        Encrypt plaintext and return self-describing ciphertext string.
        """
        pass

    @abstractmethod
    def decrypt(self, ciphertext: str, key: bytes, associated_data: Optional[bytes] = None) -> str:
        """
        Decrypt self-describing ciphertext back into plaintext.
        Raises ValueError or DecryptionError if authentication fails.
        """
        pass

    @abstractmethod
    def can_handle(self, ciphertext: str) -> bool:
        """
        Return True if this cipher can decrypt this ciphertext format.
        """
        pass
