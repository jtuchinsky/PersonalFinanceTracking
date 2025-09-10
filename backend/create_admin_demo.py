#!/usr/bin/env python3
"""
Non-interactive demo version of admin creation tool
Usage: python create_admin_demo.py [email] [name] [password]
"""

import asyncio
import sys
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def validate_email(email: str) -> bool:
    """Validate email format"""
    try:
        return "@" in email and "." in email.split("@")[1]
    except:
        return False

async def create_admin_account_demo(email, name, password):
    """Create admin account non-interactively"""
    print("🔐 Finance Tracker Admin Account Creator (Demo Mode)")
    print("=" * 60)
    
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
    
    # Validate input
    if not validate_email(email):
        print(f"❌ Invalid email format: {email}")
        await client.close()
        return False
    
    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        await client.close()
        return False
    
    if len(name.strip()) == 0:
        print("❌ Name cannot be empty")
        await client.close()
        return False
    
    # Check if email already exists
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        if existing_user.get("is_admin", False):
            print(f"❌ Admin account with email {email} already exists")
            await client.close()
            return False
        else:
            # Upgrade existing user to admin
            await db.users.update_one(
                {"email": email},
                {"$set": {
                    "is_admin": True,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            print(f"✅ User {email} upgraded to admin successfully!")
            
            # Mock welcome email
            print(f"\n📧 Mock welcome email sent to {email}")
            print("=" * 50)
            print("Subject: Welcome to Finance Tracker Admin Panel")
            print(f"Dear {existing_user['name']},")
            print("\nCongratulations! You have been granted administrator access.")
            print("You can now access the admin panel to manage users and system settings.")
            print("\nBest regards,")
            print("Finance Tracker System")
            print("=" * 50)
            
            await client.close()
            return True
    
    # Create new admin account
    try:
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "password": hash_password(password),
            "is_admin": True,
            "account_status": "active",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.users.insert_one(admin_user)
        print(f"\n✅ Admin account created successfully!")
        print(f"📧 Email: {email}")
        print(f"👤 Name: {name}")
        print(f"🔑 Admin: Yes")
        print(f"📅 Created: {admin_user['created_at']}")
        
        # Log admin creation activity
        activity = {
            "id": str(uuid.uuid4()),
            "user_id": admin_user["id"],
            "action": "admin_account_created",
            "details": f"Admin account created via demo tool for {email}",
            "timestamp": datetime.now(timezone.utc)
        }
        await db.user_activities.insert_one(activity)
        
        # Mock welcome email
        print(f"\n📧 Mock welcome email sent to {email}")
        print("=" * 50)
        print("Subject: Welcome to Finance Tracker Admin Panel")
        print(f"Dear {name},")
        print("\nCongratulations! You have been granted administrator access.")
        print("You can now access the admin panel to manage users and system settings.")
        print("\nAdmin Credentials:")
        print(f"Email: {email}")
        print(f"Password: {password}")
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
        
        admins = await db.users.find({"is_admin": True}).to_list(length=None)
        
        if not admins:
            print("No admin accounts found.")
        else:
            print(f"Found {len(admins)} admin account(s):")
            print()
            for i, admin in enumerate(admins, 1):
                status_emoji = "🟢" if admin.get("account_status") == "active" else "🔴"
                last_login = admin.get("last_login", "Never")
                if last_login != "Never":
                    last_login = last_login.strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"{i}. {status_emoji} {admin['email']}")
                print(f"   👤 Name: {admin['name']}")
                print(f"   📅 Created: {admin['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   🔐 Last Login: {last_login}")
                print(f"   📊 Status: {admin.get('account_status', 'active').title()}")
                print()
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error listing admins: {e}")

def print_usage():
    """Print usage information"""
    print("🔐 Finance Tracker Admin Management Tool (Demo)")
    print("=" * 60)
    print("Commands:")
    print("  create [email] [name] [password]  - Create a new admin account")
    print("  list                              - List existing admin accounts")
    print("  help                              - Show this help message")
    print()
    print("Examples:")
    print("  python create_admin_demo.py create admin@company.com 'John Smith' 'admin123'")
    print("  python create_admin_demo.py list")
    print()
    print("Note: This is a demo version for non-interactive environments.")
    print("For production use, use the interactive version: python create_admin.py")

async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        if len(sys.argv) != 5:
            print("❌ Usage: python create_admin_demo.py create [email] [name] [password]")
            print("Example: python create_admin_demo.py create admin@company.com 'John Smith' 'admin123'")
            return
        
        email = sys.argv[2]
        name = sys.argv[3]
        password = sys.argv[4]
        
        success = await create_admin_account_demo(email, name, password)
        if success:
            print("\n🎉 Admin account setup complete!")
            print("You can now log in to the admin panel with these credentials.")
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