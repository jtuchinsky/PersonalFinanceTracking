#!/usr/bin/env python3
"""
Enable 2FA for test admin account
"""
import asyncio
import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add parent directory to path to import shared modules
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

async def enable_2fa_for_test_admin():
    """Enable 2FA for test@admin.com"""

    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'finance_tracker')]

    try:
        from shared.twofa import generate_secret, generate_qr_code, generate_backup_codes

        # Find test admin
        admin = await db.admins.find_one({"email": "test@admin.com"})
        if not admin:
            print("❌ Test admin not found. Create it first with create_test_admin.py")
            return

        if admin.get("two_factor_enabled", False):
            print("⚠️  2FA is already enabled for test@admin.com")
            return

        # Generate 2FA credentials
        secret = generate_secret()
        qr_code_url = generate_qr_code("test@admin.com", secret)
        backup_codes = generate_backup_codes()

        # Update admin record
        await db.admins.update_one(
            {"email": "test@admin.com"},
            {"$set": {
                "two_factor_enabled": True,
                "two_factor_secret": secret,
                "backup_codes": backup_codes
            }}
        )

        print("✅ 2FA enabled for test@admin.com")
        print("📧 Email: test@admin.com")
        print("🔑 Password: admin123")
        print(f"🔐 2FA Secret: {secret}")
        print("📱 Add this secret to your authenticator app:")
        print(f"   {secret}")
        print(f"\n🛡️  Backup Codes (save these!):")
        for i, code in enumerate(backup_codes, 1):
            print(f"   {i:2d}. {code}")
        print("\n🧪 Test Login Flow:")
        print("1. Go to http://localhost:3001")
        print("2. Enter email: test@admin.com")
        print("3. Enter password: admin123")
        print("4. Enter 6-digit TOTP code from authenticator app")

    except ImportError:
        print("❌ 2FA libraries not available. Install pyotp and qrcode packages.")
        print("   pip install pyotp qrcode[pil]")

if __name__ == "__main__":
    asyncio.run(enable_2fa_for_test_admin())