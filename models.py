from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Any, Annotated
from datetime import datetime, timezone
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.str_schema()

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        field_schema.update(type="string")
        return field_schema

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return v
            raise ValueError("Invalid ObjectId")
        raise ValueError("Invalid ObjectId")

class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
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
    
    id: Optional[str] = Field(default=None, alias="_id")
    conversation_id: str
    sender_email: str
    sender_name: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
    
    id: Optional[str] = Field(default=None, alias="_id")
    participants: List[str]  # List of email addresses
    conversation_type: str = "direct"  # direct, group
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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

class UserSummary(BaseModel):
    email: str
    name: str
    profile_image: Optional[str] = None
    is_online: bool = False

class EnrichedConversationResponse(BaseModel):
    conversation_id: str
    participants: List[UserSummary]
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