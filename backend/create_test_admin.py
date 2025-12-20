#!/usr/bin/env python3
"""
Quick test admin creation script
Creates admin with known credentials for testing
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

async def create_test_admin():
    """Create a test admin with known credentials"""

    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'finance_tracker')]

    # Test admin credentials
    email = "test@admin.com"
    password = "admin123"  # Simple password for testing
    name = "Test Admin"

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Check if admin already exists
    existing = await db.admins.find_one({"email": email})
    if existing:
        print(f"✅ Test admin {email} already exists")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        await client.close()
        return

    # Create admin account
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name,
        "password": hashed_password,
        "role": "admin",
        "permissions": ["user_management", "system_stats", "view_activities"],
        "account_status": "active",
        "two_factor_enabled": False,
        "two_factor_secret": None,
        "backup_codes": None,
        "last_login": None,
        "created_by": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    await db.admins.insert_one(admin_user)

    print("✅ Test admin account created successfully!")
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print(f"👤 Name: {name}")
    print(f"🎭 Role: admin")
    print("🔐 2FA: Disabled")

    # Log admin creation activity
    activity = {
        "id": str(uuid.uuid4()),
        "admin_id": admin_user["id"],
        "action": "admin_account_created",
        "details": f"Test admin account created for {email}",
        "timestamp": datetime.now(timezone.utc)
    }
    await db.admin_activities.insert_one(activity)

    await client.close()

if __name__ == "__main__":
    asyncio.run(create_test_admin())