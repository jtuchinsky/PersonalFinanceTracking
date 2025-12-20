#!/usr/bin/env python3
"""
Setup Email-based 2FA for admin testing
"""
import asyncio
import os
import bcrypt
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def setup_email_2fa_admin():
    """Create admin with email-based 2FA"""

    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'finance_tracker')]

    # Admin credentials
    email = "admin@emailtest.com"
    password = "admin123"
    name = "Email 2FA Admin"

    # Check if admin already exists
    existing = await db.admins.find_one({"email": email})
    if existing:
        # Update existing admin to use email 2FA
        await db.admins.update_one(
            {"email": email},
            {"$set": {
                "two_factor_enabled": True,
                "two_factor_type": "email",
                "two_factor_secret": None,  # No TOTP secret for email 2FA
                "backup_codes": None,
                "phone_number": None,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        print(f"✅ Updated existing admin {email} to use EMAIL 2FA")
    else:
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create admin with email 2FA
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "password": hashed_password,
            "role": "admin",
            "permissions": ["user_management", "system_stats", "view_activities"],
            "account_status": "active",
            "two_factor_enabled": True,
            "two_factor_type": "email",  # EMAIL-based 2FA
            "two_factor_secret": None,  # No TOTP secret
            "backup_codes": None,
            "phone_number": None,
            "last_login": None,
            "created_by": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

        await db.admins.insert_one(admin_user)
        print("✅ Email 2FA admin account created successfully!")

    print("=" * 60)
    print("📧 EMAIL-BASED 2FA TEST CREDENTIALS")
    print("=" * 60)
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print(f"🎭 Role: admin")
    print("🔐 2FA Type: EMAIL")
    print("")
    print("🧪 TEST LOGIN FLOW:")
    print("1. Go to http://localhost:3001")
    print(f"2. Enter email: {email}")
    print(f"3. Enter password: {password}")
    print("4. System will 'send' email with 6-digit code (check backend logs)")
    print("5. Enter the verification code shown in logs")
    print("6. Login complete!")
    print("")
    print("💡 This demonstrates SMS/Email 2FA workflow")
    print("   (currently mock - would use real email service in production)")

if __name__ == "__main__":
    asyncio.run(setup_email_2fa_admin())