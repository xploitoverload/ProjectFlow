# app/security/two_factor_auth.py
"""
Two-Factor Authentication (2FA) implementation.
Supports TOTP (Time-based One-Time Password) authentication.
"""

import pyotp
import qrcode
from io import BytesIO
import logging
from typing import Tuple, Optional
from datetime import datetime, timedelta

logger = logging.getLogger('2fa')


class TwoFactorAuth:
    """Two-factor authentication manager."""
    
    # TOTP window (allow codes from ±30 seconds)
    TOTP_WINDOW = 1
    
    # Backup code count
    BACKUP_CODES_COUNT = 10
    
    @staticmethod
    def generate_secret() -> str:
        """
        Generate a new TOTP secret.
        
        Returns:
            Base32-encoded secret
        """
        secret = pyotp.random_base32()
        logger.debug(f"Generated new TOTP secret")
        return secret
    
    @staticmethod
    def get_provisioning_uri(secret: str, email: str, 
                             issuer: str = "Project Management") -> str:
        """
        Get provisioning URI for QR code generation.
        
        Args:
            secret: TOTP secret
            email: User email
            issuer: Issuer name
        
        Returns:
            Provisioning URI
        """
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=email,
            issuer_name=issuer
        )
        return uri
    
    @staticmethod
    def generate_qr_code(uri: str) -> BytesIO:
        """
        Generate QR code for provisioning URI.
        
        Args:
            uri: Provisioning URI
        
        Returns:
            BytesIO with PNG image
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """
        Verify TOTP token.
        
        Args:
            secret: TOTP secret
            token: Token to verify
        
        Returns:
            True if token is valid
        """
        if not secret or not token or len(token) != 6:
            return False
        
        try:
            # Verify token with window of ±1
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(token, valid_window=TwoFactorAuth.TOTP_WINDOW)
            
            if is_valid:
                logger.debug("TOTP token verified successfully")
            else:
                logger.warning("TOTP token verification failed")
            
            return is_valid
        except Exception as e:
            logger.error(f"Error verifying TOTP token: {str(e)}")
            return False
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> list:
        """
        Generate backup codes.
        
        Args:
            count: Number of codes to generate
        
        Returns:
            List of backup codes
        """
        codes = []
        for _ in range(count):
            code = pyotp.random_base32(length=8)
            codes.append(code)
        
        logger.debug(f"Generated {count} backup codes")
        return codes
    
    @staticmethod
    def verify_backup_code(backup_code: str, user_codes: list) -> Tuple[bool, list]:
        """
        Verify and consume backup code.
        
        Args:
            backup_code: Code to verify
            user_codes: List of remaining codes
        
        Returns:
            Tuple of (is_valid, updated_codes)
        """
        if backup_code in user_codes:
            user_codes.remove(backup_code)
            logger.info("Backup code used successfully")
            return True, user_codes
        
        logger.warning("Invalid backup code attempt")
        return False, user_codes
    
    @staticmethod
    def get_current_token(secret: str) -> str:
        """
        Get current TOTP token (for testing).
        
        Args:
            secret: TOTP secret
        
        Returns:
            Current token
        """
        totp = pyotp.TOTP(secret)
        return totp.now()


class TwoFactorAuthManager:
    """Manage 2FA for users."""
    
    # In production, these would be stored in database
    _user_2fa_settings = {}
    _rate_limits = {}
    
    @staticmethod
    def enable_2fa(user_id: int) -> Tuple[str, list]:
        """
        Enable 2FA for user.
        
        Args:
            user_id: User ID
        
        Returns:
            Tuple of (secret, backup_codes)
        """
        secret = TwoFactorAuth.generate_secret()
        backup_codes = TwoFactorAuth.generate_backup_codes()
        
        TwoFactorAuthManager._user_2fa_settings[user_id] = {
            'secret': secret,
            'backup_codes': backup_codes,
            'enabled': False,  # Not confirmed yet
            'created_at': datetime.now()
        }
        
        logger.info(f"2FA setup started for user {user_id}")
        
        return secret, backup_codes
    
    @staticmethod
    def confirm_2fa(user_id: int, token: str) -> bool:
        """
        Confirm 2FA setup with token.
        
        Args:
            user_id: User ID
            token: TOTP token
        
        Returns:
            True if confirmed
        """
        if user_id not in TwoFactorAuthManager._user_2fa_settings:
            return False
        
        settings = TwoFactorAuthManager._user_2fa_settings[user_id]
        
        if TwoFactorAuth.verify_token(settings['secret'], token):
            settings['enabled'] = True
            settings['confirmed_at'] = datetime.now()
            logger.info(f"2FA confirmed for user {user_id}")
            return True
        
        logger.warning(f"Failed 2FA confirmation attempt for user {user_id}")
        return False
    
    @staticmethod
    def disable_2fa(user_id: int) -> bool:
        """Disable 2FA for user."""
        if user_id in TwoFactorAuthManager._user_2fa_settings:
            del TwoFactorAuthManager._user_2fa_settings[user_id]
            logger.info(f"2FA disabled for user {user_id}")
            return True
        return False
    
    @staticmethod
    def is_2fa_enabled(user_id: int) -> bool:
        """Check if 2FA is enabled for user."""
        if user_id not in TwoFactorAuthManager._user_2fa_settings:
            return False
        return TwoFactorAuthManager._user_2fa_settings[user_id].get('enabled', False)
    
    @staticmethod
    def verify_2fa_token(user_id: int, token: str) -> bool:
        """Verify 2FA token during login."""
        if user_id not in TwoFactorAuthManager._user_2fa_settings:
            return False
        
        settings = TwoFactorAuthManager._user_2fa_settings[user_id]
        
        if not settings.get('enabled'):
            return False
        
        # Check rate limiting
        if TwoFactorAuthManager._check_rate_limit(user_id):
            logger.warning(f"2FA rate limit exceeded for user {user_id}")
            return False
        
        # Verify token
        is_valid = TwoFactorAuth.verify_token(settings['secret'], token)
        
        if is_valid:
            logger.info(f"2FA token verified for user {user_id}")
        else:
            TwoFactorAuthManager._record_failed_attempt(user_id)
        
        return is_valid
    
    @staticmethod
    def verify_backup_code(user_id: int, code: str) -> bool:
        """Verify backup code during login."""
        if user_id not in TwoFactorAuthManager._user_2fa_settings:
            return False
        
        settings = TwoFactorAuthManager._user_2fa_settings[user_id]
        
        if not settings.get('enabled'):
            return False
        
        is_valid, remaining_codes = TwoFactorAuth.verify_backup_code(
            code,
            settings['backup_codes']
        )
        
        if is_valid:
            settings['backup_codes'] = remaining_codes
            logger.info(f"Backup code used by user {user_id}")
        
        return is_valid
    
    @staticmethod
    def get_backup_codes_remaining(user_id: int) -> int:
        """Get number of remaining backup codes."""
        if user_id not in TwoFactorAuthManager._user_2fa_settings:
            return 0
        return len(TwoFactorAuthManager._user_2fa_settings[user_id]['backup_codes'])
    
    @staticmethod
    def regenerate_backup_codes(user_id: int) -> list:
        """Regenerate backup codes."""
        if user_id not in TwoFactorAuthManager._user_2fa_settings:
            return []
        
        new_codes = TwoFactorAuth.generate_backup_codes()
        TwoFactorAuthManager._user_2fa_settings[user_id]['backup_codes'] = new_codes
        
        logger.info(f"Backup codes regenerated for user {user_id}")
        
        return new_codes
    
    @staticmethod
    def _check_rate_limit(user_id: int, max_attempts: int = 5, 
                         time_window: int = 300) -> bool:
        """
        Check if user exceeded failed attempts limit.
        
        Args:
            user_id: User ID
            max_attempts: Max failed attempts
            time_window: Time window in seconds
        
        Returns:
            True if rate limited
        """
        now = datetime.now()
        
        if user_id not in TwoFactorAuthManager._rate_limits:
            return False
        
        attempts = TwoFactorAuthManager._rate_limits[user_id]
        # Remove old attempts outside time window
        attempts = [t for t in attempts if (now - t).total_seconds() < time_window]
        
        TwoFactorAuthManager._rate_limits[user_id] = attempts
        
        return len(attempts) >= max_attempts
    
    @staticmethod
    def _record_failed_attempt(user_id: int):
        """Record failed 2FA attempt."""
        if user_id not in TwoFactorAuthManager._rate_limits:
            TwoFactorAuthManager._rate_limits[user_id] = []
        
        TwoFactorAuthManager._rate_limits[user_id].append(datetime.now())


# 2FA recovery codes
class RecoveryCodes:
    """Manage recovery codes for account recovery."""
    
    @staticmethod
    def generate() -> list:
        """Generate recovery codes."""
        return [f"{pyotp.random_base32(length=4)}-{pyotp.random_base32(length=4)}" for _ in range(5)]
    
    @staticmethod
    def verify(code: str, codes: list) -> Tuple[bool, list]:
        """Verify and consume recovery code."""
        if code in codes:
            codes.remove(code)
            return True, codes
        return False, codes
