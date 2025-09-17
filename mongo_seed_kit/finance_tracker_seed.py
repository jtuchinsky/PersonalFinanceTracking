1#!/usr/bin/env python3
"""
Seed MongoDB Atlas with Finance Tracker initial data.

This script creates collections, indexes, and sample data matching
the schema described in MONGODB_SETUP.md

Usage:
    export MONGO_URL="mongodb+srv://..."
    export DB_NAME="personasal_finance-tracker"
    python finance_tracker_seed.py
"""

import os
import sys
from pathlib import Path
import asyncio
import uuid
import bcrypt
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import random

# Load environment variables from backend/.env
ROOT_DIR = Path(__file__).parent.parent / "backend"
load_dotenv(ROOT_DIR / '.env')

# Default categories from MONGODB_SETUP.md
DEFAULT_CATEGORIES = [
    {"name": "Food & Dining", "color": "#ef4444", "icon": "UtensilsCrossed"},
    {"name": "Transportation", "color": "#3b82f6", "icon": "Car"},
    {"name": "Bills & Utilities", "color": "#f59e0b", "icon": "Receipt"},
    {"name": "Shopping", "color": "#8b5cf6", "icon": "ShoppingBag"},
    {"name": "Entertainment", "color": "#06b6d4", "icon": "Film"},
    {"name": "Healthcare", "color": "#10b981", "icon": "Heart"},
    {"name": "Income", "color": "#059669", "icon": "TrendingUp"},
    {"name": "Other", "color": "#6b7280", "icon": "MoreHorizontal"}
]

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def create_indexes(db):
    """Create all indexes as defined in MONGODB_SETUP.md"""
    print("📊 Creating database indexes...")
    
    # Users collection indexes
    await db.users.create_index([("id", 1)], unique=True, name="uniq_user_id")
    await db.users.create_index([("email", 1)], unique=True, name="uniq_email")
    await db.users.create_index([("is_admin", 1)], name="idx_is_admin")
    await db.users.create_index([("account_status", 1)], name="idx_account_status")
    
    # Accounts collection indexes
    await db.accounts.create_index([("id", 1)], unique=True, name="uniq_account_id")
    await db.accounts.create_index([("user_id", 1)], name="idx_account_user_id")
    await db.accounts.create_index([("account_type", 1)], name="idx_account_type")
    await db.accounts.create_index([("user_id", 1), ("account_type", 1)], name="idx_user_account_type")
    
    # Transactions collection indexes
    await db.transactions.create_index([("id", 1)], unique=True, name="uniq_transaction_id")
    await db.transactions.create_index([("user_id", 1)], name="idx_transaction_user_id")
    await db.transactions.create_index([("account_id", 1)], name="idx_transaction_account_id")
    await db.transactions.create_index([("date", -1)], name="idx_transaction_date_desc")
    await db.transactions.create_index([("category", 1)], name="idx_transaction_category")
    await db.transactions.create_index([("transaction_type", 1)], name="idx_transaction_type")
    await db.transactions.create_index([("user_id", 1), ("date", -1)], name="idx_user_date_desc")
    await db.transactions.create_index([("user_id", 1), ("category", 1)], name="idx_user_category")
    await db.transactions.create_index([("account_id", 1), ("date", -1)], name="idx_account_date_desc")
    
    # Categories collection indexes
    await db.categories.create_index([("id", 1)], unique=True, name="uniq_category_id")
    await db.categories.create_index([("user_id", 1)], name="idx_category_user_id")
    await db.categories.create_index([("name", 1)], name="idx_category_name")
    
    # Account credentials collection indexes
    await db.account_credentials.create_index([("account_id", 1)], unique=True, name="uniq_credential_account_id")
    await db.account_credentials.create_index([("user_id", 1)], name="idx_credential_user_id")
    
    # User activities collection indexes
    await db.user_activities.create_index([("user_id", 1)], name="idx_activity_user_id")
    await db.user_activities.create_index([("timestamp", -1)], name="idx_activity_timestamp_desc")
    await db.user_activities.create_index([("action", 1)], name="idx_activity_action")
    await db.user_activities.create_index([("user_id", 1), ("timestamp", -1)], name="idx_user_activity_time_desc")
    
    # Text search indexes
    await db.transactions.create_index([("description", "text"), ("category", "text")], name="text_search_transactions")
    await db.users.create_index([("name", "text"), ("email", "text")], name="text_search_users")
    
    print("✅ Database indexes created successfully!")

async def create_sample_users(db):
    """Create sample users"""
    print("👥 Creating sample users...")
    
    users = []
    
    # Admin user
    admin_id = str(uuid.uuid4())
    admin_user = {
        "id": admin_id,
        "email": "admin@finance-tracker.com",
        "name": "System Administrator", 
        "password": hash_password("admin123"),
        "is_admin": True,
        "account_status": "active",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    users.append(admin_user)
    
    # Demo user
    demo_id = str(uuid.uuid4())
    demo_user = {
        "id": demo_id,
        "email": "demo@finance-tracker.com",
        "name": "Demo User",
        "password": hash_password("demo123"),
        "is_admin": False,
        "account_status": "active",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    users.append(demo_user)
    
    # Additional sample users
    sample_users = [
        {"email": "john.doe@example.com", "name": "John Doe", "password": "password123"},
        {"email": "jane.smith@example.com", "name": "Jane Smith", "password": "password123"},
        {"email": "mike.johnson@example.com", "name": "Mike Johnson", "password": "password123"}
    ]
    
    for user_data in sample_users:
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": user_data["email"],
            "name": user_data["name"],
            "password": hash_password(user_data["password"]),
            "is_admin": False,
            "account_status": "active",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        users.append(user)
    
    await db.users.insert_many(users)
    print(f"✅ Created {len(users)} sample users")
    
    return users

async def create_categories(db, users):
    """Create categories for all users"""
    print("🏷️ Creating categories...")
    
    categories = []
    
    for user in users:
        for cat_data in DEFAULT_CATEGORIES:
            category = {
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "name": cat_data["name"],
                "color": cat_data["color"],
                "icon": cat_data["icon"]
            }
            categories.append(category)
    
    await db.categories.insert_many(categories)
    print(f"✅ Created {len(categories)} categories")
    
    return categories

async def create_sample_accounts(db, users):
    """Create sample financial accounts"""
    print("🏦 Creating sample accounts...")
    
    accounts = []
    
    # Sample account templates
    account_templates = [
        {"name": "Chase Freedom Checking", "type": "checking", "bank": "Chase", "balance_range": (1000, 5000)},
        {"name": "Wells Fargo Savings", "type": "savings", "bank": "Wells Fargo", "balance_range": (5000, 15000)},
        {"name": "Capital One Credit Card", "type": "credit_card", "bank": "Capital One", "balance_range": (-2000, -100)},
        {"name": "Bank of America Checking", "type": "checking", "bank": "Bank of America", "balance_range": (500, 3000)},
        {"name": "Discover Savings", "type": "savings", "bank": "Discover", "balance_range": (2000, 10000)}
    ]
    
    for user in users:
        # Create 2-3 accounts per user
        num_accounts = random.randint(2, 3)
        user_templates = random.sample(account_templates, num_accounts)
        
        for template in user_templates:
            account_id = str(uuid.uuid4())
            balance = random.uniform(*template["balance_range"])
            
            account = {
                "id": account_id,
                "user_id": user["id"],
                "name": template["name"],
                "account_type": template["type"],
                "bank_name": template["bank"],
                "balance": round(balance, 2),
                "nickname": f"My {template['type'].replace('_', ' ').title()}",
                "description": f"{template['bank']} {template['type'].replace('_', ' ')} account",
                "is_default": False,
                "created_at": datetime.now(timezone.utc)
            }
            accounts.append(account)
    
    await db.accounts.insert_many(accounts)
    print(f"✅ Created {len(accounts)} sample accounts")
    
    return accounts

async def create_sample_transactions(db, users, accounts, categories):
    """Create sample transactions"""
    print("💸 Creating sample transactions...")
    
    transactions = []
    
    # Sample transaction templates
    expense_templates = [
        {"description": "Grocery Store", "category": "Food & Dining", "amount_range": (30, 150)},
        {"description": "Gas Station", "category": "Transportation", "amount_range": (25, 80)},
        {"description": "Electric Bill", "category": "Bills & Utilities", "amount_range": (80, 200)},
        {"description": "Amazon Purchase", "category": "Shopping", "amount_range": (20, 300)},
        {"description": "Movie Theater", "category": "Entertainment", "amount_range": (15, 50)},
        {"description": "Doctor Visit", "category": "Healthcare", "amount_range": (50, 250)},
        {"description": "Coffee Shop", "category": "Food & Dining", "amount_range": (3, 15)},
        {"description": "Uber Ride", "category": "Transportation", "amount_range": (10, 30)},
        {"description": "Target", "category": "Shopping", "amount_range": (25, 100)},
        {"description": "Restaurant", "category": "Food & Dining", "amount_range": (25, 80)}
    ]
    
    income_templates = [
        {"description": "Salary Deposit", "category": "Income", "amount_range": (2500, 4500)},
        {"description": "Freelance Payment", "category": "Income", "amount_range": (500, 1500)},
        {"description": "Interest Payment", "category": "Income", "amount_range": (5, 50)}
    ]
    
    # Create transactions for the last 90 days
    for user in users:
        user_accounts = [acc for acc in accounts if acc["user_id"] == user["id"]]
        user_categories = [cat for cat in categories if cat["user_id"] == user["id"]]
        
        # Create 30-50 transactions per user
        num_transactions = random.randint(30, 50)
        
        for _ in range(num_transactions):
            # Random date in the last 90 days
            days_ago = random.randint(0, 90)
            transaction_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
            
            # Choose random account
            account = random.choice(user_accounts)
            
            # 80% expenses, 20% income
            if random.random() < 0.8:
                # Expense transaction
                template = random.choice(expense_templates)
                amount = -abs(random.uniform(*template["amount_range"]))
                transaction_type = "debit"
            else:
                # Income transaction
                template = random.choice(income_templates)
                amount = abs(random.uniform(*template["amount_range"]))
                transaction_type = "credit"
            
            transaction = {
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "account_id": account["id"],
                "amount": round(amount, 2),
                "description": template["description"],
                "category": template["category"],
                "transaction_type": transaction_type,
                "date": transaction_date,
                "created_at": datetime.now(timezone.utc)
            }
            transactions.append(transaction)
    
    # Insert in batches for better performance
    batch_size = 100
    for i in range(0, len(transactions), batch_size):
        batch = transactions[i:i+batch_size]
        await db.transactions.insert_many(batch)
    
    print(f"✅ Created {len(transactions)} sample transactions")
    
    return transactions

async def create_user_activities(db, users):
    """Create sample user activity logs"""
    print("📊 Creating user activity logs...")
    
    activities = []
    
    activity_templates = [
        {"action": "login", "details": "User logged in successfully"},
        {"action": "logout", "details": "User logged out"},
        {"action": "account_created", "details": "New financial account created"},
        {"action": "transaction_created", "details": "New transaction recorded"},
        {"action": "profile_updated", "details": "User profile information updated"}
    ]
    
    for user in users:
        # Create 5-10 activities per user
        num_activities = random.randint(5, 10)
        
        for _ in range(num_activities):
            days_ago = random.randint(0, 30)
            activity_time = datetime.now(timezone.utc) - timedelta(days=days_ago)
            
            template = random.choice(activity_templates)
            
            activity = {
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "action": template["action"],
                "details": template["details"],
                "timestamp": activity_time
            }
            activities.append(activity)
    
    await db.user_activities.insert_many(activities)
    print(f"✅ Created {len(activities)} user activity logs")

async def update_account_balances(db, transactions):
    """Update account balances based on transactions"""
    print("💰 Updating account balances...")
    
    # Group transactions by account
    account_totals = {}
    for transaction in transactions:
        account_id = transaction["account_id"]
        if account_id not in account_totals:
            account_totals[account_id] = 0
        account_totals[account_id] += transaction["amount"]
    
    # Update each account's balance
    for account_id, total_change in account_totals.items():
        await db.accounts.update_one(
            {"id": account_id},
            {"$inc": {"balance": total_change}}
        )
    
    print(f"✅ Updated balances for {len(account_totals)} accounts")

async def main():
    """Main seeding function"""
    print("🚀 Starting MongoDB Atlas Finance Tracker Seeding")
    print("=" * 60)
    
    # Get connection details
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'personasal_finance-tracker')
    
    if not mongo_url:
        print("❌ Error: MONGO_URL environment variable not found")
        sys.exit(1)
    
    print(f"🔗 Connecting to MongoDB Atlas...")
    print(f"📊 Database: {db_name}")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")
        
        # Check if database already has data
        collections = await db.list_collection_names()
        if collections:
            print(f"⚠️  Database already contains {len(collections)} collections")
            print("🔄 Continuing with sample data creation...")
        
        # Create indexes first
        await create_indexes(db)
        
        # Create sample data
        users = await create_sample_users(db)
        categories = await create_categories(db, users)
        accounts = await create_sample_accounts(db, users)
        transactions = await create_sample_transactions(db, users, accounts, categories)
        await create_user_activities(db, users)
        await update_account_balances(db, transactions)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 Database seeding completed successfully!")
        print("=" * 60)
        print(f"👥 Users created: {len(users)}")
        print(f"🏷️ Categories created: {len(categories)}")
        print(f"🏦 Accounts created: {len(accounts)}")
        print(f"💸 Transactions created: {len(transactions)}")
        print(f"📊 Activity logs created: {len(users) * 7}")  # Approximate
        
        print("\n📧 Sample Login Credentials:")
        print("Admin: admin@finance-tracker.com / admin123")
        print("Demo User: demo@finance-tracker.com / demo123")
        print("Sample Users: john.doe@example.com / password123")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())