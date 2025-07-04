from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from models import ChatMessage, Conversation, User, MessageResponse, ConversationResponse, EnrichedConversationResponse, UserSummary
from database import get_chat_messages_collection, get_conversations_collection, get_users_collection

class ChatService:
    
    @staticmethod
    async def create_or_get_conversation(participant1: str, participant2: str) -> str:
        """Create a new conversation or get existing one between two users"""
        conversations_collection = await get_conversations_collection()
        
        # Check if conversation already exists
        existing_conversation = await conversations_collection.find_one({
            "participants": {"$all": [participant1, participant2]},
            "conversation_type": "direct"
        })
        
        if existing_conversation:
            return str(existing_conversation["_id"])
        
        # Create new conversation
        conversation_data = {
            "participants": [participant1, participant2],
            "conversation_type": "direct", 
            "created_at": datetime.now(timezone.utc),
            "unread_count": {participant1: 0, participant2: 0}
        }
        
        result = await conversations_collection.insert_one(conversation_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def send_message(conversation_id: str, sender_email: str, sender_name: str, 
                          message_content: str, message_type: str = "text", 
                          reply_to: Optional[str] = None) -> ChatMessage:
        """Send a message to a conversation"""
        chat_messages_collection = await get_chat_messages_collection()
        conversations_collection = await get_conversations_collection()
        
        # Create message
        message_data = {
            "conversation_id": conversation_id,
            "sender_email": sender_email,
            "sender_name": sender_name,
            "message": message_content,
            "timestamp": datetime.now(timezone.utc),
            "message_type": message_type,
            "edited": False,
            "reply_to": reply_to
        }
        
        # Insert message
        result = await chat_messages_collection.insert_one(message_data)
        
        # Create response object
        message = ChatMessage(
            id=str(result.inserted_id),
            conversation_id=conversation_id,
            sender_email=sender_email,
            sender_name=sender_name,
            message=message_content,
            timestamp=message_data["timestamp"],
            message_type=message_type,
            reply_to=reply_to
        )
        
        # Update conversation with last message info
        await conversations_collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$set": {
                    "last_message": message_content,
                    "last_message_time": message.timestamp,
                    "last_message_sender": sender_email
                },
                "$inc": {
                    f"unread_count.{sender_email}": 0  # Don't increment for sender
                }
            }
        )
        
        # Increment unread count for other participants
        conversation = await conversations_collection.find_one({"_id": ObjectId(conversation_id)})
        if conversation:
            for participant in conversation["participants"]:
                if participant != sender_email:
                    await conversations_collection.update_one(
                        {"_id": ObjectId(conversation_id)},
                        {"$inc": {f"unread_count.{participant}": 1}}
                    )
        
        return message
    
    @staticmethod
    async def get_conversation_messages(conversation_id: str, skip: int = 0, limit: int = 50) -> List[MessageResponse]:
        """Get messages from a conversation with pagination"""
        chat_messages_collection = await get_chat_messages_collection()
        
        cursor = chat_messages_collection.find(
            {"conversation_id": conversation_id}
        ).sort("timestamp", -1).skip(skip).limit(limit)
        
        messages = []
        async for message in cursor:
            messages.append(MessageResponse(
                id=str(message["_id"]),
                conversation_id=message["conversation_id"],
                sender_email=message["sender_email"],
                sender_name=message["sender_name"],
                message=message["message"],
                timestamp=message["timestamp"],
                message_type=message["message_type"],
                edited=message.get("edited", False),
                reply_to=message.get("reply_to")
            ))
        
        return list(reversed(messages))  # Return in chronological order
    
    @staticmethod
    async def get_user_conversations(user_email: str) -> List[ConversationResponse]:
        """Get all conversations for a user"""
        conversations_collection = await get_conversations_collection()
        
        cursor = conversations_collection.find(
            {"participants": user_email}
        ).sort("last_message_time", -1)
        
        conversations = []
        async for conv in cursor:
            conversations.append(ConversationResponse(
                conversation_id=str(conv["_id"]),
                participants=conv["participants"],
                last_message=conv.get("last_message"),
                last_message_time=conv.get("last_message_time"),
                last_message_sender=conv.get("last_message_sender"),
                unread_count=conv.get("unread_count", {}).get(user_email, 0)
            ))
        
        return conversations
    
    @staticmethod
    async def get_user_conversations_enriched(user_email: str) -> List[EnrichedConversationResponse]:
        """Get all conversations for a user with full user details"""
        conversations_collection = await get_conversations_collection()
        users_collection = await get_users_collection()
        
        cursor = conversations_collection.find(
            {"participants": user_email}
        ).sort("last_message_time", -1)
        
        conversations = []
        async for conv in cursor:
            # Get user details for all participants
            participant_users = []
            for participant_email in conv["participants"]:
                user_data = await users_collection.find_one({"email": participant_email})
                if user_data:
                    participant_users.append(UserSummary(
                        email=user_data["email"],
                        name=user_data["name"],
                        profile_image=user_data.get("profile_image"),
                        is_online=user_data.get("is_online", False)
                    ))
                else:
                    # Fallback for users not found in database
                    participant_users.append(UserSummary(
                        email=participant_email,
                        name=participant_email.split('@')[0],  # Use email prefix as name
                        profile_image=None,
                        is_online=False
                    ))
            
            conversations.append(EnrichedConversationResponse(
                conversation_id=str(conv["_id"]),
                participants=participant_users,
                last_message=conv.get("last_message"),
                last_message_time=conv.get("last_message_time"),
                last_message_sender=conv.get("last_message_sender"),
                unread_count=conv.get("unread_count", {}).get(user_email, 0)
            ))
        
        return conversations
    
    @staticmethod
    async def mark_conversation_as_read(conversation_id: str, user_email: str):
        """Mark all messages in a conversation as read for a user"""
        conversations_collection = await get_conversations_collection()
        
        await conversations_collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {f"unread_count.{user_email}": 0}}
        )
    
    @staticmethod
    async def update_user_online_status(email: str, is_online: bool, socket_id: Optional[str] = None):
        """Update user's online status and socket ID"""
        users_collection = await get_users_collection()
        
        update_data = {
            "is_online": is_online,
            "last_seen": datetime.now(timezone.utc)
        }
        
        if socket_id:
            update_data["socket_id"] = socket_id
        elif not is_online:
            update_data["socket_id"] = None
        
        await users_collection.update_one(
            {"email": email},
            {"$set": update_data},
            upsert=True
        )
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        users_collection = await get_users_collection()
        user_data = await users_collection.find_one({"email": email})
        
        if user_data:
            # Convert ObjectId to string for Pydantic v2 compatibility
            if "_id" in user_data and isinstance(user_data["_id"], ObjectId):
                user_data["_id"] = str(user_data["_id"])
            return User(**user_data)
        return None
    
    @staticmethod
    async def create_user(email: str, name: str, profile_image: Optional[str] = None) -> User:
        """Create a new user"""
        users_collection = await get_users_collection()
        
        user_data = {
            "email": email,
            "name": name,
            "profile_image": profile_image,
            "is_online": False,
            "last_seen": None,
            "socket_id": None
        }
        
        result = await users_collection.insert_one(user_data)
        
        user = User(
            id=str(result.inserted_id),
            email=email,
            name=name,
            profile_image=profile_image,
            is_online=False
        )
        
        return user 