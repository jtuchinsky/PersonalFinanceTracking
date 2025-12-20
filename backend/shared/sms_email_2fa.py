"""
SMS/Email-based 2FA implementation
"""
import random
import string
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SMSEmail2FA:
    def __init__(self):
        # In-memory storage for verification codes (use Redis in production)
        self.verification_codes: Dict[str, Dict[str, Any]] = {}
        self.code_expiry_minutes = 5

    def generate_verification_code(self, length: int = 6) -> str:
        """Generate a random verification code"""
        return ''.join(random.choices(string.digits, k=length))

    async def send_sms_code(self, phone_number: str, user_name: str) -> str:
        """
        Send SMS verification code (mock implementation)
        In production, integrate with Twilio, AWS SNS, etc.
        """
        code = self.generate_verification_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.code_expiry_minutes)

        # Store verification code
        self.verification_codes[phone_number] = {
            'code': code,
            'expires_at': expires_at,
            'attempts': 0,
            'type': 'sms'
        }

        # Mock SMS sending (replace with real SMS service)
        print("📱 MOCK SMS SENT:")
        print(f"To: {phone_number}")
        print(f"Message: Your Finance Tracker admin verification code is: {code}")
        print(f"This code expires in {self.code_expiry_minutes} minutes.")
        print("=" * 50)

        return code

    async def send_email_code(self, email: str, user_name: str) -> str:
        """
        Send email verification code (mock implementation)
        In production, integrate with SendGrid, AWS SES, etc.
        """
        code = self.generate_verification_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.code_expiry_minutes)

        # Store verification code
        self.verification_codes[email] = {
            'code': code,
            'expires_at': expires_at,
            'attempts': 0,
            'type': 'email'
        }

        # Mock email sending (replace with real email service)
        print("📧 MOCK EMAIL SENT:")
        print(f"To: {email}")
        print(f"Subject: Your Finance Tracker Admin Verification Code")
        print(f"Body:")
        print(f"Dear {user_name},")
        print(f"")
        print(f"Your verification code is: {code}")
        print(f"")
        print(f"This code will expire in {self.code_expiry_minutes} minutes.")
        print(f"If you did not request this code, please contact support.")
        print(f"")
        print(f"Best regards,")
        print(f"Finance Tracker Admin Team")
        print("=" * 50)

        return code

    def verify_code(self, identifier: str, provided_code: str) -> bool:
        """
        Verify the provided code against stored code
        identifier: phone number or email
        """
        stored_data = self.verification_codes.get(identifier)

        if not stored_data:
            return False

        # Check if code has expired
        if datetime.now(timezone.utc) > stored_data['expires_at']:
            # Clean up expired code
            del self.verification_codes[identifier]
            return False

        # Check attempt limit (prevent brute force)
        if stored_data['attempts'] >= 3:
            del self.verification_codes[identifier]
            return False

        # Increment attempt counter
        stored_data['attempts'] += 1

        # Verify code
        if stored_data['code'] == provided_code:
            # Clean up successful verification
            del self.verification_codes[identifier]
            return True

        return False

    def cleanup_expired_codes(self):
        """Clean up expired verification codes"""
        current_time = datetime.now(timezone.utc)
        expired_keys = [
            key for key, data in self.verification_codes.items()
            if current_time > data['expires_at']
        ]

        for key in expired_keys:
            del self.verification_codes[key]

    def get_remaining_time(self, identifier: str) -> Optional[int]:
        """Get remaining time for verification code in seconds"""
        stored_data = self.verification_codes.get(identifier)
        if not stored_data:
            return None

        remaining = stored_data['expires_at'] - datetime.now(timezone.utc)
        return max(0, int(remaining.total_seconds()))


# Global instance for the application
sms_email_2fa = SMSEmail2FA()


# Cleanup task to run periodically
async def cleanup_expired_codes_task():
    """Background task to clean up expired codes"""
    while True:
        sms_email_2fa.cleanup_expired_codes()
        await asyncio.sleep(60)  # Clean up every minute