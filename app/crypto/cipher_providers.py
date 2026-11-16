"""
Authenticated Symmetric Field Cipher Providers.
Implements AES-256-GCM, ChaCha20-Poly1305, Fernet (backward compatibility), and Custom Cipher hooks.
"""

import base64
import os
import secrets
from typing import Optional, Callable
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.fernet import Fernet
from app.crypto.base import BaseFieldCipher


def _normalize_key(key: bytes, required_len: int = 32) -> bytes:
    """Normalize input key to exactly required_len bytes."""
    if len(key) == required_len:
        return key
    # If 44-char url-safe base64 (e.g. Fernet key)
    try:
        decoded = base64.urlsafe_b64decode(key)
        if len(decoded) == required_len:
            return decoded
        if len(decoded) > required_len:
            return decoded[:required_len]
    except Exception:
        pass
    import hashlib
    return hashlib.sha256(key).digest()[:required_len]


class AES256GCMCipher(BaseFieldCipher):
    """
    NIST SP 800-38D AES-256 in Galois/Counter Mode (GCM).
    Provides authenticated encryption with associated data (AEAD).
    Format: gcm$<b64_nonce>$<b64_ciphertext_with_tag>
    """
    name = "aes_256_gcm"

    def encrypt(self, plaintext: str, key: bytes, associated_data: Optional[bytes] = None) -> str:
        if plaintext is None:
            return None
        k = _normalize_key(key, 32)
        aesgcm = AESGCM(k)
        nonce = secrets.token_bytes(12)  # 96-bit nonce
        ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), associated_data)
        return f"gcm${base64.b64encode(nonce).decode('utf-8')}${base64.b64encode(ct).decode('utf-8')}"

    def decrypt(self, ciphertext: str, key: bytes, associated_data: Optional[bytes] = None) -> str:
        if ciphertext is None:
            return None
        if not self.can_handle(ciphertext):
            raise ValueError("Invalid AES-256-GCM ciphertext format")
        parts = ciphertext.split('$')
        if len(parts) != 3:
            raise ValueError("Malformed AES-256-GCM payload")
        nonce = base64.b64decode(parts[1])
        ct = base64.b64decode(parts[2])
        k = _normalize_key(key, 32)
        aesgcm = AESGCM(k)
        pt = aesgcm.decrypt(nonce, ct, associated_data)
        return pt.decode('utf-8')

    def can_handle(self, ciphertext: str) -> bool:
        return bool(ciphertext and ciphertext.startswith('gcm$'))


class ChaCha20Poly1305Cipher(BaseFieldCipher):
    """
    RFC 8439 ChaCha20-Poly1305 Authenticated Stream Cipher.
    High performance and immune to cache timing attacks on software implementations.
    Format: chacha$<b64_nonce>$<b64_ciphertext_with_tag>
    """
    name = "chacha20_poly1305"

    def encrypt(self, plaintext: str, key: bytes, associated_data: Optional[bytes] = None) -> str:
        if plaintext is None:
            return None
        k = _normalize_key(key, 32)
        cipher = ChaCha20Poly1305(k)
        nonce = secrets.token_bytes(12)  # 96-bit nonce
        ct = cipher.encrypt(nonce, plaintext.encode('utf-8'), associated_data)
        return f"chacha${base64.b64encode(nonce).decode('utf-8')}${base64.b64encode(ct).decode('utf-8')}"

    def decrypt(self, ciphertext: str, key: bytes, associated_data: Optional[bytes] = None) -> str:
        if ciphertext is None:
            return None
        if not self.can_handle(ciphertext):
            raise ValueError("Invalid ChaCha20-Poly1305 ciphertext format")
        parts = ciphertext.split('$')
        if len(parts) != 3:
            raise ValueError("Malformed ChaCha20-Poly1305 payload")
        nonce = base64.b64decode(parts[1])
        ct = base64.b64decode(parts[2])
        k = _normalize_key(key, 32)
        cipher = ChaCha20Poly1305(k)
        pt = cipher.decrypt(nonce, ct, associated_data)
        return pt.decode('utf-8')

    def can_handle(self, ciphertext: str) -> bool:
        return bool(ciphertext and ciphertext.startswith('chacha$'))


class FernetCipher(BaseFieldCipher):
    """
    Fernet Symmetric Cipher (AES-128-CBC + HMAC-SHA256).
    Provides 100% backward compatibility for existing encrypted database fields.
    Format: Fernet token (e.g. gAAAAAB...) or fernet$<token>
    """
    name = "fernet"

    def _get_fernet(self, key: bytes) -> Fernet:
        # Fernet requires 32-byte urlsafe base64 string
        if len(key) == 44:
            try:
                base64.urlsafe_b64decode(key)
                return Fernet(key)
            except Exception:
                pass
        import hashlib
        h = hashlib.sha256(key).digest()
        fernet_key = base64.urlsafe_b64encode(h)
        return Fernet(fernet_key)

    def encrypt(self, plaintext: str, key: bytes, associated_data: Optional[bytes] = None) -> str:
        if plaintext is None:
            return None
        f = self._get_fernet(key)
        return f.encrypt(plaintext.encode('utf-8')).decode('utf-8')

    def decrypt(self, ciphertext: str, key: bytes, associated_data: Optional[bytes] = None) -> str:
        if ciphertext is None:
            return None
        token = ciphertext
        if token.startswith('fernet$'):
            token = token[7:]
        f = self._get_fernet(key)
        return f.decrypt(token.encode('utf-8')).decode('utf-8')

    def can_handle(self, ciphertext: str) -> bool:
        if not ciphertext:
            return False
        if ciphertext.startswith('fernet$'):
            return True
        if ciphertext.startswith('gAAAAA') and len(ciphertext) >= 100:
            return True
        return False


class CustomCipherProvider(BaseFieldCipher):
    """
    Extensible Custom Cipher Provider.
    Allows end users to plug in custom cryptographic ciphers, HSM, KMS,
    or quantum-safe ciphers by subclassing or providing callables.
    """
    name = "custom"

    def __init__(
        self,
        name: str = "custom",
        encrypt_fn: Optional[Callable[[str, bytes, Optional[bytes]], str]] = None,
        decrypt_fn: Optional[Callable[[str, bytes, Optional[bytes]], str]] = None,
        prefix: str = "custom$"
    ):
        self.name = name
        self._encrypt_fn = encrypt_fn
        self._decrypt_fn = decrypt_fn
        self.prefix = prefix

    def encrypt(self, plaintext: str, key: bytes, associated_data: Optional[bytes] = None) -> str:
        if self._encrypt_fn:
            res = self._encrypt_fn(plaintext, key, associated_data)
            if not res.startswith(self.prefix):
                return f"{self.prefix}{res}"
            return res
        raise NotImplementedError("Custom cipher must implement encrypt() or provide encrypt_fn")

    def decrypt(self, ciphertext: str, key: bytes, associated_data: Optional[bytes] = None) -> str:
        if not self.can_handle(ciphertext):
            raise ValueError("Ciphertext not handled by this custom provider")
        if self._decrypt_fn:
            payload = ciphertext[len(self.prefix):] if ciphertext.startswith(self.prefix) else ciphertext
            return self._decrypt_fn(payload, key, associated_data)
        raise NotImplementedError("Custom cipher must implement decrypt() or provide decrypt_fn")

    def can_handle(self, ciphertext: str) -> bool:
        return bool(ciphertext and ciphertext.startswith(self.prefix))
