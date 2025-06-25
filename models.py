from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: str
    name: str
    profile_image: Optional[str] = None
    is_online: bool = False
    last_seen: Optional[datetime] = None
    socket_id: Optional[str] = None

class ChatMessage(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    conversation_id: str
    sender_email: str
    sender_name: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_type: str = "text"  # text, image, file, etc.
    edited: bool = False
    edited_at: Optional[datetime] = None
    reply_to: Optional[str] = None  # ID of message being replied to

class Conversation(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    participants: List[str]  # List of email addresses
    conversation_type: str = "direct"  # direct, group
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    last_message_sender: Optional[str] = None
    unread_count: dict = {}  # {email: count}

class MessageRequest(BaseModel):
    to_email: str
    message: str
    message_type: str = "text"
    reply_to: Optional[str] = None

class ConversationResponse(BaseModel):
    conversation_id: str
    participants: List[str]
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    last_message_sender: Optional[str] = None
    unread_count: int = 0

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_email: str
    sender_name: str
    message: str
    timestamp: datetime
    message_type: str
    edited: bool
    reply_to: Optional[str] = None 