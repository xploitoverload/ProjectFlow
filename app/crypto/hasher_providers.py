"""
Standard and Extensible Password Hasher Providers.
Implements Argon2id, PBKDF2-HMAC-SHA512, Scrypt, Bcrypt, and Custom/User-Defined Algorithms.
"""

import hmac
import hashlib
import secrets
from typing import Optional, Callable
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from app.crypto.base import BasePasswordHasher

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False


class Argon2idHasher(BasePasswordHasher):
    """
    Argon2id Password Hasher.
    Winner of the Password Hashing Competition (PHC) and OWASP Top Recommendation.
    Memory-hard, highly resistant to GPU/ASIC brute-force cracking.
    """
    name = "argon2id"

    def __init__(self, time_cost: int = 3, memory_cost: int = 65536, parallelism: int = 4, hash_len: int = 32, salt_len: int = 16):
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.hash_len = hash_len
        self.salt_len = salt_len
        self._ph = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len
        )

    def hash(self, password: str) -> str:
        return self._ph.hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        if not hashed or not password:
            return False
        try:
            return self._ph.verify(hashed, password)
        except (VerifyMismatchError, InvalidHash):
            return False
        except Exception:
            return False

    def needs_rehash(self, hashed: str) -> bool:
        try:
            return self._ph.check_needs_rehash(hashed)
        except Exception:
            return True

    def can_handle(self, hashed: str) -> bool:
        return bool(hashed and (hashed.startswith('$argon2id$') or hashed.startswith('$argon2i$') or hashed.startswith('$argon2d$')))


class PBKDF2SHA512Hasher(BasePasswordHasher):
    """
    PBKDF2-HMAC-SHA512 Password Hasher.
    FIPS 140-2 and NIST SP 800-132 compliant.
    OWASP recommended minimum: 600,000 iterations for SHA-512.
    Format: pbkdf2:sha512:600000$<salt_hex>$<hash_hex>
    """
    name = "pbkdf2_sha512"

    def __init__(self, iterations: int = 600000, salt_bytes: int = 16, key_len: int = 64):
        self.iterations = iterations
        self.salt_bytes = salt_bytes
        self.key_len = key_len

    def hash(self, password: str) -> str:
        salt = secrets.token_bytes(self.salt_bytes)
        derived = hashlib.pbkdf2_hmac(
            'sha512',
            password.encode('utf-8'),
            salt,
            self.iterations,
            dklen=self.key_len
        )
        return f"pbkdf2:sha512:{self.iterations}${salt.hex()}${derived.hex()}"

    def verify(self, password: str, hashed: str) -> bool:
        if not hashed or not password:
            return False
        try:
            # Handle standard custom format: pbkdf2:sha512:<iters>$<salt_hex>$<hash_hex>
            if hashed.startswith('pbkdf2:sha512:'):
                parts = hashed.split('$')
                if len(parts) == 3:
                    prefix = parts[0]  # pbkdf2:sha512:<iters>
                    salt = bytes.fromhex(parts[1])
                    expected_hash = bytes.fromhex(parts[2])
                    iters = int(prefix.split(':')[2])
                    derived = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, iters, dklen=len(expected_hash))
                    return hmac.compare_digest(derived, expected_hash)
            
            # Handle Werkzeug legacy pbkdf2 format e.g. pbkdf2:sha256:260000$salt$hash
            if hashed.startswith('pbkdf2:'):
                from werkzeug.security import check_password_hash
                return check_password_hash(hashed, password)
        except Exception:
            return False
        return False

    def needs_rehash(self, hashed: str) -> bool:
        if not hashed.startswith(f"pbkdf2:sha512:{self.iterations}$"):
            return True
        return False

    def can_handle(self, hashed: str) -> bool:
        return bool(hashed and hashed.startswith('pbkdf2:'))


class ScryptHasher(BasePasswordHasher):
    """
    Scrypt Password Hasher.
    Memory-hard key derivation function (RFC 7914).
    Format: scrypt:<n>:<r>:<p>$<salt_hex>$<hash_hex>
    """
    name = "scrypt"

    def __init__(self, n: int = 16384, r: int = 8, p: int = 1, salt_bytes: int = 16, key_len: int = 64):
        self.n = n
        self.r = r
        self.p = p
        self.salt_bytes = salt_bytes
        self.key_len = key_len

    def hash(self, password: str) -> str:
        salt = secrets.token_bytes(self.salt_bytes)
        derived = hashlib.scrypt(
            password.encode('utf-8'),
            salt=salt,
            n=self.n,
            r=self.r,
            p=self.p,
            maxmem=64 * 1024 * 1024,
            dklen=self.key_len
        )
        return f"scrypt:{self.n}:{self.r}:{self.p}${salt.hex()}${derived.hex()}"

    def verify(self, password: str, hashed: str) -> bool:
        if not hashed or not password:
            return False
        try:
            if not hashed.startswith('scrypt:'):
                return False
            parts = hashed.split('$')
            if len(parts) != 3:
                return False
            params = parts[0].split(':')
            n = int(params[1])
            r = int(params[2])
            p = int(params[3])
            salt = bytes.fromhex(parts[1])
            expected = bytes.fromhex(parts[2])
            derived = hashlib.scrypt(
                password.encode('utf-8'),
                salt=salt,
                n=n,
                r=r,
                p=p,
                maxmem=64 * 1024 * 1024,
                dklen=len(expected)
            )
            return hmac.compare_digest(derived, expected)
        except Exception:
            return False

    def needs_rehash(self, hashed: str) -> bool:
        prefix = f"scrypt:{self.n}:{self.r}:{self.p}$"
        return not (hashed and hashed.startswith(prefix))

    def can_handle(self, hashed: str) -> bool:
        return bool(hashed and hashed.startswith('scrypt:'))


class BcryptHasher(BasePasswordHasher):
    """
    Bcrypt Password Hasher.
    Battle-tested industry standard with configurable work factor.
    Format: $2b$<rounds>$<salt+hash>
    """
    name = "bcrypt"

    def __init__(self, rounds: int = 12):
        self.rounds = rounds

    def hash(self, password: str) -> str:
        if not HAS_BCRYPT:
            raise RuntimeError("bcrypt package is not installed.")
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify(self, password: str, hashed: str) -> bool:
        if not HAS_BCRYPT or not hashed or not password:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    def needs_rehash(self, hashed: str) -> bool:
        if not HAS_BCRYPT or not hashed:
            return True
        try:
            # Check cost parameter e.g. $2b$12$...
            parts = hashed.split('$')
            if len(parts) >= 3:
                cost = int(parts[2])
                return cost != self.rounds
        except Exception:
            return True
        return False

    def can_handle(self, hashed: str) -> bool:
        return bool(hashed and (hashed.startswith('$2b$') or hashed.startswith('$2a$') or hashed.startswith('$2y$')))


class CustomHasherProvider(BasePasswordHasher):
    """
    Extensible Custom Hasher Provider.
    Allows end users to plug in ANY custom cryptographic algorithm, HSM hook,
    or proprietary hashing mechanism by subclassing or supplying callables.
    
    Example:
        class QuantumResistantHasher(CustomHasherProvider):
            name = "sphincs_plus"
            ...
    """
    name = "custom"

    def __init__(
        self,
        name: str = "custom",
        hash_fn: Optional[Callable[[str], str]] = None,
        verify_fn: Optional[Callable[[str, str], bool]] = None,
        prefix: str = "custom:"
    ):
        self.name = name
        self._hash_fn = hash_fn
        self._verify_fn = verify_fn
        self.prefix = prefix

    def hash(self, password: str) -> str:
        if self._hash_fn:
            res = self._hash_fn(password)
            if not res.startswith(self.prefix):
                return f"{self.prefix}{res}"
            return res
        raise NotImplementedError("Custom hasher must implement hash() or provide hash_fn")

    def verify(self, password: str, hashed: str) -> bool:
        if not hashed or not password:
            return False
        if not self.can_handle(hashed):
            return False
        if self._verify_fn:
            payload = hashed[len(self.prefix):] if hashed.startswith(self.prefix) else hashed
            return self._verify_fn(password, payload)
        raise NotImplementedError("Custom hasher must implement verify() or provide verify_fn")

    def needs_rehash(self, hashed: str) -> bool:
        return not bool(hashed and hashed.startswith(self.prefix))

    def can_handle(self, hashed: str) -> bool:
        return bool(hashed and hashed.startswith(self.prefix))
