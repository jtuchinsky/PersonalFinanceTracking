from cryptography.fernet import Fernet
import base64
import os
from datetime import datetime, timezone
from .models import UserActivity
from .database import db

# Encryption settings for account credentials
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "finance-tracker-encryption-key-2025")
# Generate a proper Fernet key from the encryption key
fernet_key = base64.urlsafe_b64encode(ENCRYPTION_KEY.ljust(32)[:32].encode())
cipher_suite = Fernet(fernet_key)

def encrypt_credential(credential: str) -> str:
    """Encrypt account credentials"""
    return cipher_suite.encrypt(credential.encode()).decode()

def decrypt_credential(encrypted_credential: str) -> str:
    """Decrypt account credentials"""
    return cipher_suite.decrypt(encrypted_credential.encode()).decode()

async def log_user_activity(user_id: str, action: str, details: str, ip_address: str = None):
    """Log user activity for admin monitoring"""
    activity = UserActivity(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address
    )

    activity_dict = activity.model_dump()
    await db.user_activities.insert_one(activity_dict)
    return activity