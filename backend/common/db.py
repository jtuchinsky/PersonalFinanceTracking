import os
from functools import lru_cache
from pymongo import MongoClient

from dotenv import load_dotenv
load_dotenv()  # <— add this

import os
from functools import lru_cache
from pymongo import MongoClient

@lru_cache(maxsize=1)
def _client() -> MongoClient:
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI not set")
    return MongoClient(uri)

def get_db():
    name = os.getenv("MONGO_DB_NAME", "personal_finance")
    return _client()[name]
