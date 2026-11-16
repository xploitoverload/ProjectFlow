"""
ProjectFlow Pluggable Cryptographic Subsystem.
Supports Argon2id, PBKDF2-SHA512, Scrypt, Bcrypt, AES-256-GCM, ChaCha20-Poly1305, Fernet,
and custom user-provided hashing and cipher implementations.
"""

from app.crypto.base import BasePasswordHasher, BaseFieldCipher
from app.crypto.hasher_providers import (
    Argon2idHasher,
    PBKDF2SHA512Hasher,
    ScryptHasher,
    BcryptHasher,
    CustomHasherProvider,
)
from app.crypto.cipher_providers import (
    AES256GCMCipher,
    ChaCha20Poly1305Cipher,
    FernetCipher,
    CustomCipherProvider,
)
from app.crypto.manager import CryptoManager, crypto_manager

__all__ = [
    "BasePasswordHasher",
    "BaseFieldCipher",
    "Argon2idHasher",
    "PBKDF2SHA512Hasher",
    "ScryptHasher",
    "BcryptHasher",
    "CustomHasherProvider",
    "AES256GCMCipher",
    "ChaCha20Poly1305Cipher",
    "FernetCipher",
    "CustomCipherProvider",
    "CryptoManager",
    "crypto_manager",
]
