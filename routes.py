from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import logging

from models import (
    User, MessageResponse, ConversationResponse, 
    MessageRequest
)
from chat_service import ChatService
from auth import verify_token, create_access_token

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from JWT token"""
    try:
        email = verify_token(credentials.credentials)
        return email
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/auth/login")
async def login(email: str, name: str, profile_image: Optional[str] = None):
    """
    Login or create user and return JWT token
    This is a simplified login - in production you'd verify against your existing user system
    """
    try:
        # Check if user exists, if not create one
        user = await ChatService.get_user_by_email(email)
        if not user:
            user = await ChatService.create_user(email, name, profile_image)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "email": user.email,
                "name": user.name,
                "profile_image": user.profile_image
            }
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.get("/users/me")
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """Get current user information"""
    try:
        user = await ChatService.get_user_by_email(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "email": user.email,
            "name": user.name,
            "profile_image": user.profile_image,
            "is_online": user.is_online,
            "last_seen": user.last_seen
        }
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user info")

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(current_user: str = Depends(get_current_user)):
    """Get all conversations for the current user"""
    try:
        conversations = await ChatService.get_user_conversations(current_user)
        return conversations
    except Exception as e:
        logger.error(f"Get conversations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: str = Depends(get_current_user)
):
    """Get messages from a specific conversation"""
    try:
        messages = await ChatService.get_conversation_messages(conversation_id, skip, limit)
        return messages
    except Exception as e:
        logger.error(f"Get messages error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@router.post("/conversations/{conversation_id}/mark-read")
async def mark_conversation_read(
    conversation_id: str,
    current_user: str = Depends(get_current_user)
):
    """Mark a conversation as read for the current user"""
    try:
        await ChatService.mark_conversation_as_read(conversation_id, current_user)
        return {"message": "Conversation marked as read"}
    except Exception as e:
        logger.error(f"Mark as read error: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark conversation as read")

@router.post("/conversations/start")
async def start_conversation(
    to_email: str,
    current_user: str = Depends(get_current_user)
):
    """Start a new conversation with another user"""
    try:
        # Check if the other user exists
        other_user = await ChatService.get_user_by_email(to_email)
        if not other_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create or get existing conversation
        conversation_id = await ChatService.create_or_get_conversation(current_user, to_email)
        
        return {
            "conversation_id": conversation_id,
            "participants": [current_user, to_email]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start conversation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start conversation")

@router.post("/messages/send")
async def send_message_rest(
    message_request: MessageRequest,
    current_user: str = Depends(get_current_user)
):
    """Send a message via REST API (alternative to Socket.IO)"""
    try:
        # Get sender user info
        sender_user = await ChatService.get_user_by_email(current_user)
        if not sender_user:
            raise HTTPException(status_code=404, detail="Sender not found")
        
        # Check if recipient exists
        recipient_user = await ChatService.get_user_by_email(message_request.to_email)
        if not recipient_user:
            raise HTTPException(status_code=404, detail="Recipient not found")
        
        # Create or get conversation
        conversation_id = await ChatService.create_or_get_conversation(
            current_user, message_request.to_email
        )
        
        # Send message
        message = await ChatService.send_message(
            conversation_id=conversation_id,
            sender_email=current_user,
            sender_name=sender_user.name,
            message_content=message_request.message,
            message_type=message_request.message_type,
            reply_to=message_request.reply_to
        )
        
        return {
            "id": str(message.id),
            "conversation_id": conversation_id,
            "sender_email": current_user,
            "sender_name": sender_user.name,
            "message": message_request.message,
            "timestamp": message.timestamp,
            "message_type": message_request.message_type,
            "reply_to": message_request.reply_to
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send message REST error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.get("/users/search")
async def search_users(
    query: str,
    current_user: str = Depends(get_current_user)
):
    """Search for users by email or name"""
    try:
        # This is a basic implementation - you might want to integrate with your existing user system
        # For now, we'll just return users from the chat system
        from database import get_users_collection
        users_collection = await get_users_collection()
        
        # Search by email or name (case insensitive)
        cursor = users_collection.find({
            "$and": [
                {"email": {"$ne": current_user}},  # Exclude current user
                {
                    "$or": [
                        {"email": {"$regex": query, "$options": "i"}},
                        {"name": {"$regex": query, "$options": "i"}}
                    ]
                }
            ]
        }).limit(10)
        
        users = []
        async for user in cursor:
            users.append({
                "email": user["email"],
                "name": user["name"],
                "profile_image": user.get("profile_image"),
                "is_online": user.get("is_online", False)
            })
        
        return users
    except Exception as e:
        logger.error(f"Search users error: {e}")
        raise HTTPException(status_code=500, detail="Failed to search users") 