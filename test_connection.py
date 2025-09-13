#!/usr/bin/env python3
"""
Test MongoDB Atlas connection
"""

import asyncio
import sys
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

async def test_connection():
    """Test MongoDB connection"""
    print("🔗 Testing MongoDB Atlas Connection")
    print("=" * 50)
    
    # Get connection details
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'personasal_finance-tracker')
    
    if not mongo_url:
        print("❌ Error: MONGO_URL environment variable not found")
        return False
    
    print(f"🔗 Connecting to: {mongo_url[:20]}...")
    print(f"📊 Database: {db_name}")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection by pinging
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # List collections
        collections = await db.list_collection_names()
        print(f"📋 Found {len(collections)} collections:")
        for collection in collections:
            count = await db[collection].count_documents({})
            print(f"   • {collection}: {count} documents")
        
        # Test basic operations
        print("\n🧪 Testing basic operations...")
        
        # Insert test document
        test_collection = db.connection_test
        test_doc = {
            "test": True,
            "message": "Connection test successful",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Insert test successful: {result.inserted_id}")
        
        # Read test document
        found_doc = await test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("✅ Read test successful")
        
        # Delete test document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Delete test successful")
        
        if client:
            client.close()
        print("\n🎉 All tests passed! MongoDB Atlas connection is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if not success:
        sys.exit(1)