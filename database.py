from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import asyncio

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.DATABASE_NAME]
    
    # Create indexes for better performance
    await db.database.chat_messages.create_index([("conversation_id", 1), ("timestamp", -1)])
    await db.database.conversations.create_index([("participants", 1)])
    await db.database.conversations.create_index([("last_message_time", -1)])
    
    print("Connected to MongoDB")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

# Collections
async def get_chat_messages_collection():
    database = await get_database()
    return database.chat_messages

async def get_conversations_collection():
    database = await get_database()
    return database.conversations

async def get_users_collection():
    database = await get_database()
    return database.users 