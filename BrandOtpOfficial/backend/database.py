"""
MongoDB Database Configuration
Handles connection to MongoDB Atlas and collection definitions
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== MONGODB CONNECTION STRING =====
# Get from environment variable or use default
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    # Default connection string (REPLACE WITH YOUR ACTUAL URI)
    "mongodb+srv://username:password@cluster.mongodb.net/brandotp?retryWrites=true&w=majority"
)

# Database name
DATABASE_NAME = os.getenv("DATABASE_NAME", "brandotp")

# ===== CREATE MONGODB CLIENT =====
try:
    # Create async MongoDB client
    client = AsyncIOMotorClient(MONGODB_URI)
    
    # Get database
    db = client[DATABASE_NAME]
    
    # Test connection
    client.admin.command('ping')
    logger.info("✅ MongoDB connected successfully")
    logger.info(f"✅ Using database: {DATABASE_NAME}")
    
    # ===== DEFINE COLLECTIONS =====
    users_collection = db.users
    transactions_collection = db.transactions
    numbers_collection = db.numbers
    orders_collection = db.orders
    
    logger.info("✅ All collections initialized")
    
except ConnectionFailure as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    logger.warning("⚠️ Running without database - data will not be saved!")
    
    # Set collections to None if connection fails
    db = None
    users_collection = None
    transactions_collection = None
    numbers_collection = None
    orders_collection = None
    
except Exception as e:
    logger.error(f"❌ Unexpected database error: {e}")
    db = None
    users_collection = None
    transactions_collection = None
    numbers_collection = None
    orders_collection = None


# ===== HELPER FUNCTIONS =====

async def check_connection():
    """Check if database connection is alive"""
    try:
        await client.admin.command('ping')
        return True
    except:
        return False


async def get_user_by_id(user_id: str):
    """Get user by ID"""
    if users_collection is None:
        return None
    return await users_collection.find_one({"_id": user_id})


async def get_user_by_email(email: str):
    """Get user by email"""
    if users_collection is None:
        return None
    return await users_collection.find_one({"email": email})


async def update_user_balance(user_id: str, new_balance: float):
    """Update user balance"""
    if users_collection is None:
        return False
    
    result = await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"balance": new_balance}}
    )
    return result.modified_count > 0


async def create_transaction(transaction_data: dict):
    """Create new transaction record"""
    if transactions_collection is None:
        return None
    
    result = await transactions_collection.insert_one(transaction_data)
    return result.inserted_id


# ===== EXPORT =====
__all__ = [
    'db',
    'users_collection',
    'transactions_collection',
    'numbers_collection',
    'orders_collection',
    'check_connection',
    'get_user_by_id',
    'get_user_by_email',
    'update_user_balance',
    'create_transaction'
]
