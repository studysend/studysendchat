#!/usr/bin/env python3
"""
Test script to verify Chat Socket Backend setup
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_database_connection():
    """Test MongoDB connection"""
    try:
        print("🔌 Testing MongoDB connection...")
        from database import connect_to_mongo, close_mongo_connection, get_database
        
        await connect_to_mongo()
        db = await get_database()
        
        # Test basic operations
        await db.test_collection.insert_one({"test": "connection", "timestamp": datetime.utcnow()})
        await db.test_collection.delete_many({"test": "connection"})
        
        await close_mongo_connection()
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

async def test_chat_service():
    """Test chat service functionality"""
    try:
        print("🔧 Testing Chat Service...")
        from database import connect_to_mongo, close_mongo_connection
        from chat_service import ChatService
        
        await connect_to_mongo()
        
        # Test user creation
        user1 = await ChatService.create_user("test1@example.com", "Test User 1")
        user2 = await ChatService.create_user("test2@example.com", "Test User 2")
        
        # Test conversation creation
        conversation_id = await ChatService.create_or_get_conversation(
            user1.email, user2.email
        )
        
        # Test message sending
        message = await ChatService.send_message(
            conversation_id=conversation_id,
            sender_email=user1.email,
            sender_name=user1.name,
            message_content="Hello, this is a test message!"
        )
        
        # Test message retrieval
        messages = await ChatService.get_conversation_messages(conversation_id)
        
        # Clean up test data
        from database import get_users_collection, get_conversations_collection, get_chat_messages_collection
        users_col = await get_users_collection()
        conv_col = await get_conversations_collection()
        msg_col = await get_chat_messages_collection()
        
        await users_col.delete_many({"email": {"$in": ["test1@example.com", "test2@example.com"]}})
        await conv_col.delete_many({"_id": {"$exists": True}})
        await msg_col.delete_many({"conversation_id": conversation_id})
        
        await close_mongo_connection()
        print("✅ Chat Service test successful!")
        return True
    except Exception as e:
        print(f"❌ Chat Service test failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("🌍 Testing environment configuration...")
    
    try:
        from config import settings
        
        required_settings = [
            'MONGODB_URL',
            'DATABASE_NAME', 
            'JWT_SECRET_KEY',
            'JWT_ALGORITHM'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not hasattr(settings, setting) or not getattr(settings, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            print(f"❌ Missing environment settings: {', '.join(missing_settings)}")
            return False
        
        print("✅ Environment configuration is valid!")
        return True
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("📦 Testing module imports...")
    
    modules_to_test = [
        'fastapi',
        'socketio',
        'motor',
        'pymongo',
        'pydantic',
        'jose',
        'passlib',
        'uvicorn'
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            __import__(module)
        except ImportError:
            failed_imports.append(module)
    
    if failed_imports:
        print(f"❌ Failed to import: {', '.join(failed_imports)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required modules imported successfully!")
    return True

async def main():
    """Run all tests"""
    print("🧪 Starting Chat Socket Backend Setup Tests")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment),
        ("Database Connection", test_database_connection),
        ("Chat Service", test_chat_service)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your chat backend is ready to run.")
        print("\n🚀 To start the server:")
        print("   Development: python run.py --reload")
        print("   Production:  python run.py --production")
        print("   Docker:      docker-compose up")
        print("\n📖 Open client_example.html in your browser to test the chat functionality.")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before running the server.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main()) 