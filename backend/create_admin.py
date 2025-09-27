#!/usr/bin/env python3
"""
Command-line tool to create admin accounts for Finance Tracker
Usage: python create_admin.py
"""

import asyncio
import sys
import os
from pathlib import Path
from getpass import getpass
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import EmailStr, ValidationError
import bcrypt
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add parent directory to path to import from server.py
sys.path.append(str(Path(__file__).parent))

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def validate_email(email: str) -> bool:
    """Validate email format"""
    try:
        # Simple email validation
        return "@" in email and "." in email.split("@")[1]
    except:
        return False

async def create_admin_account():
    """Create admin account interactively"""
    print("🔐 Finance Tracker Admin Account Creator")
    print("=" * 50)
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ Error: MONGO_URL environment variable not found")
        return False
    
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME', 'finance_tracker')]
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return False
    
    # Get admin details
    print("\n📝 Enter Admin Account Details:")
    
    # Email
    while True:
        email = input("Email: ").strip()
        if not email:
            print("❌ Email is required")
            continue
        
        if not validate_email(email):
            print("❌ Invalid email format")
            continue
        
        # Check if admin email already exists
        existing_admin = await db.admins.find_one({"email": email})
        if existing_admin:
            print(f"❌ Admin account with email {email} already exists")
            continue
        break
    
    # Name
    while True:
        name = input("Full Name: ").strip()
        if not name:
            print("❌ Name is required")
            continue
        break
    
    # Password
    while True:
        password = getpass("Password (min 8 characters): ")
        if len(password) < 8:
            print("❌ Password must be at least 8 characters")
            continue
        
        confirm_password = getpass("Confirm Password: ")
        if password != confirm_password:
            print("❌ Passwords do not match")
            continue
        break
    
    # Create admin account
    try:
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "password": hash_password(password),
            "role": "admin",
            "permissions": ["user_management", "system_stats", "view_activities"],
            "account_status": "active",
            "last_login": None,
            "created_by": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

        await db.admins.insert_one(admin_user)
        print(f"\n✅ Admin account created successfully!")
        print(f"📧 Email: {email}")
        print(f"👤 Name: {name}")
        print(f"🔑 Admin: Yes")
        print(f"📅 Created: {admin_user['created_at']}")
        
        # Log admin creation activity
        activity = {
            "id": str(uuid.uuid4()),
            "admin_id": admin_user["id"],
            "action": "admin_account_created",
            "details": f"Admin account created via command line for {email}",
            "timestamp": datetime.now(timezone.utc)
        }
        await db.admin_activities.insert_one(activity)
        
        # Mock welcome email
        print(f"\n📧 Mock welcome email sent to {email}")
        print("=" * 50)
        print("Subject: Welcome to Finance Tracker Admin Panel")
        print(f"Dear {name},")
        print("\nCongratulations! You have been granted administrator access.")
        print("You can now access the admin panel to manage users and system settings.")
        print("\nBest regards,")
        print("Finance Tracker System")
        print("=" * 50)
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin account: {e}")
        await client.close()
        return False

async def list_admins():
    """List all existing admin accounts"""
    print("👥 Existing Admin Accounts")
    print("=" * 50)
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ Error: MONGO_URL environment variable not found")
        return
    
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME', 'finance_tracker')]
        
        admins = await db.admins.find({}).to_list(length=None)

        if not admins:
            print("No admin accounts found.")
        else:
            for admin in admins:
                status_emoji = "🟢" if admin.get("account_status") == "active" else "🔴"
                role = admin.get("role", "admin")
                print(f"{status_emoji} {admin['email']} ({admin['name']}) - Role: {role} - Created: {admin['created_at']}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error listing admins: {e}")

def print_usage():
    """Print usage information"""
    print("🔐 Finance Tracker Admin Management Tool")
    print("=" * 50)
    print("Commands:")
    print("  create  - Create a new admin account")
    print("  list    - List existing admin accounts")
    print("  help    - Show this help message")
    print("\nUsage:")
    print("  python create_admin.py [command]")
    print("  python create_admin.py create")
    print("  python create_admin.py list")

async def main():
    """Main function"""
    if len(sys.argv) < 2:
        command = "create"  # Default command
    else:
        command = sys.argv[1].lower()
    
    if command == "create":
        success = await create_admin_account()
        if success:
            print("\n🎉 Admin account setup complete!")
            print("You can now log in to the admin panel.")
        else:
            print("\n❌ Admin account creation failed.")
            sys.exit(1)
    
    elif command == "list":
        await list_admins()
    
    elif command == "help":
        print_usage()
    
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())