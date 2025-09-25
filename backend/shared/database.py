from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# Global variables for client and db
client = None
db = None

def get_database():
    """Get database instance, initializing if needed"""
    global client, db
    if client is None:
        mongo_url = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URL')
        if not mongo_url:
            raise ValueError("MongoDB URI not found. Set MONGODB_URI or MONGO_URL environment variable")

        # Connection options to handle SSL issues
        connection_options = {
            'serverSelectionTimeoutMS': 5000,
            'connectTimeoutMS': 10000,
            'socketTimeoutMS': 10000,
        }

        # For MongoDB Atlas connections, add TLS settings
        if 'mongodb+srv' in mongo_url or 'ssl=true' in mongo_url:
            connection_options.update({
                'tls': True,
                'tlsAllowInvalidCertificates': True,
                'tlsAllowInvalidHostnames': True
            })

        try:
            client = AsyncIOMotorClient(mongo_url, **connection_options)
        except Exception as e:
            print(f"Failed to connect with SSL options: {e}")
            # Last resort: try with minimal options
            client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)

        db_name = os.environ.get('DB_NAME', 'finance_tracker')
        db = client[db_name]

    return db

# Initialize db on import for backwards compatibility
try:
    db = get_database()
except Exception as e:
    print(f"Warning: Could not initialize database on import: {e}")
    db = None

async def shutdown_db_client():
    global client
    if client:
        client.close()