from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection with retry logic"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to MongoDB (attempt {attempt + 1}/{max_retries})")
            db.client = AsyncIOMotorClient(settings.MONGODB_URL)
            db.database = db.client[settings.DATABASE_NAME]
            
            # Test the connection
            await db.client.admin.command('ping')
            
            # Create indexes for better performance
            await db.database.chat_messages.create_index([("conversation_id", 1), ("timestamp", -1)])
            await db.database.conversations.create_index([("participants", 1)])
            await db.database.conversations.create_index([("last_message_time", -1)])
            
            logger.info("Connected to MongoDB successfully")
            return
            
        except Exception as e:
            logger.error(f"MongoDB connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("All MongoDB connection attempts failed")
                raise e

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

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