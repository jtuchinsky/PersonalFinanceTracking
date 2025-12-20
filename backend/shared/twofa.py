"""
Two-Factor Authentication utilities for admin accounts
"""
import pyotp
import qrcode
import io
import base64
import secrets
from typing import List, Tuple


def generate_secret() -> str:
    """Generate a new TOTP secret"""
    return pyotp.random_base32()


def generate_qr_code(email: str, secret: str, issuer_name: str = "Finance Tracker Admin") -> str:
    """Generate QR code URL for TOTP setup"""
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=email,
        issuer_name=issuer_name
    )

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 string
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def verify_totp(secret: str, token: str) -> bool:
    """Verify a TOTP token"""
    if not secret or not token:
        return False

    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 1 window (30 seconds) of tolerance
    except Exception:
        return False


def generate_backup_codes(count: int = 8) -> List[str]:
    """Generate backup codes for 2FA recovery"""
    codes = []
    for _ in range(count):
        # Generate 8-character alphanumeric codes
        code = secrets.token_hex(4).upper()
        codes.append(code)
    return codes


def verify_backup_code(backup_codes: List[str], provided_code: str) -> Tuple[bool, List[str]]:
    """
    Verify a backup code and return updated backup codes list
    Returns (is_valid, updated_backup_codes)
    """
    if not backup_codes or not provided_code:
        return False, backup_codes

    provided_code = provided_code.upper().strip()

    if provided_code in backup_codes:
        # Remove the used backup code
        updated_codes = [code for code in backup_codes if code != provided_code]
        return True, updated_codes

    return False, backup_codes


def is_valid_totp_format(token: str) -> bool:
    """Check if a token has valid TOTP format (6 digits)"""
    return token.isdigit() and len(token) == 6


def is_valid_backup_code_format(code: str) -> bool:
    """Check if a code has valid backup code format (8 hex characters)"""
    if not code or len(code) != 8:
        return False

    try:
        int(code, 16)  # Check if it's valid hexadecimal
        return True
    except ValueError:
        return False