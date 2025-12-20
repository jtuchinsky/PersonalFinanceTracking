#!/usr/bin/env python3
"""
Advanced Admin Account Creation Tool for Finance Tracker
Supports 2FA setup and comprehensive admin management

Usage:
    python create_admin_advanced.py create
    python create_admin_advanced.py create --with-2fa
    python create_admin_advanced.py list
    python create_admin_advanced.py disable-2fa <admin_email>
    python create_admin_advanced.py enable-2fa <admin_email>
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path
from getpass import getpass
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import EmailStr, ValidationError
import bcrypt
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from typing import Optional, List

# Add parent directory to path to import shared modules
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
        return "@" in email and "." in email.split("@")[1]
    except:
        return False

async def get_db_connection():
    """Get database connection"""
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ Error: MONGO_URL environment variable not found")
        sys.exit(1)

    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME', 'finance_tracker')]
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        return client, db
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        sys.exit(1)

async def create_admin_account(enable_2fa: bool = False):
    """Create admin account with optional 2FA setup"""
    print("🔐 Finance Tracker Advanced Admin Account Creator")
    print("=" * 60)

    client, db = await get_db_connection()

    # Get admin details
    print("\n📝 Enter Admin Account Details:")

    # Email
    while True:
        email = input("📧 Admin Email: ").strip().lower()
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
        name = input("👤 Full Name: ").strip()
        if not name:
            print("❌ Name is required")
            continue
        break

    # Role
    print("\n🎭 Available Roles:")
    print("  1. admin - Standard admin privileges")
    print("  2. super_admin - Full system privileges")

    while True:
        role_choice = input("🎯 Choose role (1 or 2): ").strip()
        if role_choice == "1":
            role = "admin"
            permissions = ["user_management", "system_stats", "view_activities"]
            break
        elif role_choice == "2":
            role = "super_admin"
            permissions = ["user_management", "system_stats", "view_activities", "admin_management", "system_config"]
            break
        else:
            print("❌ Please choose 1 or 2")

    # Password
    while True:
        password = getpass("🔑 Password (min 8 characters): ")
        if len(password) < 8:
            print("❌ Password must be at least 8 characters")
            continue

        confirm_password = getpass("🔑 Confirm Password: ")
        if password != confirm_password:
            print("❌ Passwords do not match")
            continue
        break

    # 2FA Setup
    two_factor_enabled = False
    two_factor_secret = None
    backup_codes = None

    if enable_2fa:
        print(f"\n🔐 Setting up Two-Factor Authentication for {email}")
        try:
            from shared.twofa import generate_secret, generate_qr_code, generate_backup_codes

            two_factor_secret = generate_secret()
            qr_code_url = generate_qr_code(email, two_factor_secret)
            backup_codes = generate_backup_codes()

            print("\n📱 2FA Setup Instructions:")
            print("1. Install an authenticator app (Google Authenticator, Authy, etc.)")
            print("2. Scan this QR code or manually enter the secret:")
            print(f"   Secret: {two_factor_secret}")
            print("\n3. QR Code (base64 - you can decode this to display the QR code)")
            print(f"   {qr_code_url[:100]}...")

            print(f"\n🛡️  Backup Codes (save these securely!):")
            for i, code in enumerate(backup_codes, 1):
                print(f"   {i:2d}. {code}")

            # Verify setup
            while True:
                setup_2fa = input(f"\n✅ Have you set up the authenticator app? (y/n): ").lower()
                if setup_2fa in ['y', 'yes']:
                    # Test TOTP code
                    from shared.twofa import verify_totp
                    test_code = input("🔢 Enter a code from your authenticator app to verify setup: ")
                    if verify_totp(two_factor_secret, test_code):
                        two_factor_enabled = True
                        print("✅ 2FA verification successful!")
                        break
                    else:
                        print("❌ Invalid code. Please try again.")
                elif setup_2fa in ['n', 'no']:
                    print("⚠️  2FA setup cancelled. Admin will be created without 2FA.")
                    two_factor_secret = None
                    backup_codes = None
                    break
                else:
                    print("❌ Please answer y or n")

        except ImportError:
            print("❌ 2FA libraries not available. Install pyotp and qrcode packages.")
            print("   pip install pyotp qrcode[pil]")
            enable_2fa = False

    # Create admin account
    try:
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "password": hash_password(password),
            "role": role,
            "permissions": permissions,
            "account_status": "active",
            "two_factor_enabled": two_factor_enabled,
            "two_factor_secret": two_factor_secret,
            "backup_codes": backup_codes,
            "last_login": None,
            "created_by": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

        await db.admins.insert_one(admin_user)

        print(f"\n✅ Admin account created successfully!")
        print(f"📧 Email: {email}")
        print(f"👤 Name: {name}")
        print(f"🎭 Role: {role}")
        print(f"🔐 2FA Enabled: {'Yes' if two_factor_enabled else 'No'}")
        print(f"📅 Created: {admin_user['created_at']}")

        # Log admin creation activity
        activity = {
            "id": str(uuid.uuid4()),
            "admin_id": admin_user["id"],
            "action": "admin_account_created",
            "details": f"Admin account created via command line for {email} with role {role}",
            "timestamp": datetime.now(timezone.utc)
        }
        await db.admin_activities.insert_one(activity)

        if two_factor_enabled:
            print(f"\n🛡️  IMPORTANT: Save your backup codes!")
            print("These codes can be used if you lose access to your authenticator app:")
            for i, code in enumerate(backup_codes, 1):
                print(f"   {i:2d}. {code}")

        await client.close()
        return True

    except Exception as e:
        print(f"❌ Error creating admin account: {e}")
        await client.close()
        return False

async def list_admins():
    """List all existing admin accounts with enhanced details"""
    print("👥 Admin Accounts in System")
    print("=" * 80)

    client, db = await get_db_connection()

    try:
        admins = await db.admins.find({}).to_list(length=None)

        if not admins:
            print("No admin accounts found.")
        else:
            print(f"{'Status':<8} {'Email':<30} {'Name':<25} {'Role':<12} {'2FA':<5} {'Created':<20}")
            print("-" * 100)

            for admin in admins:
                status_emoji = "🟢" if admin.get("account_status") == "active" else "🔴"
                role = admin.get("role", "admin")
                two_fa = "✅" if admin.get("two_factor_enabled", False) else "❌"
                created = admin.get("created_at", "Unknown")
                if isinstance(created, datetime):
                    created = created.strftime("%Y-%m-%d %H:%M")

                print(f"{status_emoji:<8} {admin['email']:<30} {admin['name']:<25} {role:<12} {two_fa:<5} {str(created):<20}")

        await client.close()

    except Exception as e:
        print(f"❌ Error listing admins: {e}")

async def manage_admin_2fa(email: str, action: str):
    """Enable or disable 2FA for an existing admin"""
    client, db = await get_db_connection()

    try:
        admin = await db.admins.find_one({"email": email.lower()})
        if not admin:
            print(f"❌ Admin with email {email} not found")
            await client.close()
            return False

        if action == "enable":
            if admin.get("two_factor_enabled", False):
                print(f"⚠️  2FA is already enabled for {email}")
                await client.close()
                return True

            print(f"🔐 Enabling 2FA for admin: {admin['name']} ({email})")

            try:
                from shared.twofa import generate_secret, generate_qr_code, generate_backup_codes

                secret = generate_secret()
                qr_code_url = generate_qr_code(email, secret)
                backup_codes = generate_backup_codes()

                print(f"\n📱 2FA Setup for {admin['name']}:")
                print(f"Secret: {secret}")
                print(f"QR Code: {qr_code_url[:100]}...")
                print(f"\n🛡️  Backup Codes:")
                for i, code in enumerate(backup_codes, 1):
                    print(f"   {i:2d}. {code}")

                # Update admin record
                await db.admins.update_one(
                    {"id": admin["id"]},
                    {"$set": {
                        "two_factor_enabled": True,
                        "two_factor_secret": secret,
                        "backup_codes": backup_codes,
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )

                print(f"✅ 2FA enabled for {email}")

            except ImportError:
                print("❌ 2FA libraries not available. Install pyotp and qrcode packages.")
                return False

        elif action == "disable":
            if not admin.get("two_factor_enabled", False):
                print(f"⚠️  2FA is already disabled for {email}")
                await client.close()
                return True

            print(f"🔓 Disabling 2FA for admin: {admin['name']} ({email})")

            # Update admin record
            await db.admins.update_one(
                {"id": admin["id"]},
                {"$set": {
                    "two_factor_enabled": False,
                    "two_factor_secret": None,
                    "backup_codes": None,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )

            print(f"✅ 2FA disabled for {email}")

        # Log activity
        activity = {
            "id": str(uuid.uuid4()),
            "admin_id": admin["id"],
            "action": f"2fa_{action}d_cli",
            "details": f"2FA {action}d via command line for {email}",
            "timestamp": datetime.now(timezone.utc)
        }
        await db.admin_activities.insert_one(activity)

        await client.close()
        return True

    except Exception as e:
        print(f"❌ Error managing 2FA: {e}")
        await client.close()
        return False

def print_usage():
    """Print usage information"""
    print("🔐 Finance Tracker Advanced Admin Management Tool")
    print("=" * 60)
    print("Commands:")
    print("  create           - Create a new admin account")
    print("  create --with-2fa - Create admin account with 2FA setup")
    print("  list             - List all admin accounts with details")
    print("  enable-2fa EMAIL - Enable 2FA for existing admin")
    print("  disable-2fa EMAIL- Disable 2FA for existing admin")
    print("  help             - Show this help message")
    print("\nUsage:")
    print("  python create_admin_advanced.py create")
    print("  python create_admin_advanced.py create --with-2fa")
    print("  python create_admin_advanced.py list")
    print("  python create_admin_advanced.py enable-2fa admin@example.com")
    print("  python create_admin_advanced.py disable-2fa admin@example.com")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Advanced Admin Account Management")
    parser.add_argument("command", choices=["create", "list", "enable-2fa", "disable-2fa", "help"],
                       help="Command to execute")
    parser.add_argument("email", nargs="?", help="Admin email (for 2FA commands)")
    parser.add_argument("--with-2fa", action="store_true", help="Enable 2FA during account creation")

    if len(sys.argv) < 2:
        print_usage()
        return

    args = parser.parse_args()

    if args.command == "create":
        print(f"🚀 Creating admin account{'with 2FA' if args.with_2fa else ''}...")
        success = await create_admin_account(enable_2fa=args.with_2fa)
        if success:
            print("\n🎉 Admin account creation complete!")
            print("The admin can now log in to the admin panel.")
        else:
            print("\n❌ Admin account creation failed.")
            sys.exit(1)

    elif args.command == "list":
        await list_admins()

    elif args.command == "enable-2fa":
        if not args.email:
            print("❌ Email address is required for enable-2fa command")
            print("Usage: python create_admin_advanced.py enable-2fa admin@example.com")
            sys.exit(1)
        await manage_admin_2fa(args.email, "enable")

    elif args.command == "disable-2fa":
        if not args.email:
            print("❌ Email address is required for disable-2fa command")
            print("Usage: python create_admin_advanced.py disable-2fa admin@example.com")
            sys.exit(1)
        await manage_admin_2fa(args.email, "disable")

    elif args.command == "help":
        print_usage()

    else:
        print(f"❌ Unknown command: {args.command}")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)