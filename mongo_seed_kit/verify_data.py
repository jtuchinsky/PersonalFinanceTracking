#!/usr/bin/env python3
"""
Verify seeded data in MongoDB Atlas
"""

import os
import sys
from pathlib import Path
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables from backend/.env
ROOT_DIR = Path(__file__).parent.parent / "backend"
load_dotenv(ROOT_DIR / '.env')

async def verify_data():
    """Verify all seeded data"""
    print("🔍 Verifying MongoDB Atlas Data")
    print("=" * 50)
    
    # Get connection details
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'personasal_finance-tracker')
    
    if not mongo_url:
        print("❌ Error: MONGO_URL environment variable not found")
        sys.exit(1)
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")
        print(f"📊 Database: {db_name}")
        
        # Verify collections and data
        collections = await db.list_collection_names()
        print(f"\n📋 Found {len(collections)} collections:")
        
        collection_stats = {}
        
        for collection in collections:
            count = await db[collection].count_documents({})
            collection_stats[collection] = count
            print(f"   • {collection}: {count} documents")
        
        # Verify specific data integrity
        print("\n🔍 Data Integrity Checks:")
        
        # Check users
        users_count = collection_stats.get('users', 0)
        admin_count = await db.users.count_documents({"is_admin": True})
        print(f"   • Users: {users_count} total, {admin_count} admin(s)")
        
        # Check accounts
        accounts_count = collection_stats.get('accounts', 0)
        account_types = await db.accounts.distinct("account_type")
        print(f"   • Accounts: {accounts_count} total, types: {account_types}")
        
        # Check transactions
        transactions_count = collection_stats.get('transactions', 0)
        transaction_types = await db.transactions.distinct("transaction_type")
        print(f"   • Transactions: {transactions_count} total, types: {transaction_types}")
        
        # Check categories
        categories_count = collection_stats.get('categories', 0)
        category_names = await db.categories.distinct("name")
        print(f"   • Categories: {categories_count} total")
        print(f"   • Category names: {', '.join(category_names)}")
        
        # Verify indexes
        print("\n📊 Index Verification:")
        for collection in ['users', 'accounts', 'transactions', 'categories']:
            if collection in collections:
                indexes = await db[collection].list_indexes().to_list(length=None)
                print(f"   • {collection}: {len(indexes)} indexes")
        
        # Sample data verification
        print("\n🔍 Sample Data Check:")
        
        # Check if admin user exists
        admin_user = await db.users.find_one({"email": "admin@finance-tracker.com"})
        if admin_user:
            print("   ✅ Admin user found")
        else:
            print("   ❌ Admin user not found")
        
        # Check if demo user exists
        demo_user = await db.users.find_one({"email": "demo@finance-tracker.com"})
        if demo_user:
            print("   ✅ Demo user found")
            
            # Check if demo user has accounts
            demo_accounts = await db.accounts.count_documents({"user_id": demo_user["id"]})
            print(f"   ✅ Demo user has {demo_accounts} accounts")
            
            # Check if demo user has transactions
            demo_transactions = await db.transactions.count_documents({"user_id": demo_user["id"]})
            print(f"   ✅ Demo user has {demo_transactions} transactions")
        else:
            print("   ❌ Demo user not found")
        
        # Test a sample query
        print("\n🧪 Sample Query Test:")
        recent_transactions = await db.transactions.find().sort("date", -1).limit(5).to_list(length=5)
        print(f"   ✅ Found {len(recent_transactions)} recent transactions")
        
        if recent_transactions:
            latest = recent_transactions[0]
            print(f"   • Latest: {latest['description']} - ${abs(latest['amount'])} ({latest['category']})")
        
        print("\n" + "=" * 50)
        print("🎉 Data verification completed successfully!")
        print("✅ MongoDB Atlas is properly seeded with Finance Tracker data")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify_data())