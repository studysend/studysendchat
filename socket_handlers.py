import socketio
from typing import Dict
from datetime import timezone
from auth import verify_token
from chat_service import ChatService
from models import MessageRequest
import asyncio
import logging

logger = logging.getLogger(__name__)

# Store user socket mappings
connected_users: Dict[str, str] = {}  # {email: socket_id}

class SocketHandler:
    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.sio.event
        async def connect(sid, environ, auth):
            """Handle client connection"""
            try:
                # Verify JWT token
                token = auth.get('token') if auth else None
                if not token:
                    await self.sio.disconnect(sid)
                    return False
                
                email = verify_token(token)
                
                # Store user connection
                connected_users[email] = sid
                
                # Update user online status
                await ChatService.update_user_online_status(email, True, sid)
                
                # Join user to their personal room
                await self.sio.enter_room(sid, f"user:{email}")
                
                # Get user's conversations and join those rooms
                conversations = await ChatService.get_user_conversations(email)
                for conv in conversations:
                    await self.sio.enter_room(sid, f"conversation:{conv.conversation_id}")
                
                # Notify other users that this user is online
                await self.sio.emit('user_online', {'email': email}, skip_sid=sid)
                
                logger.info(f"User {email} connected with socket {sid}")
                
            except Exception as e:
                logger.error(f"Connection error: {e}")
                await self.sio.disconnect(sid)
                return False
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection"""
            try:
                # Find user by socket ID
                user_email = None
                for email, socket_id in connected_users.items():
                    if socket_id == sid:
                        user_email = email
                        break
                
                if user_email:
                    # Remove from connected users
                    del connected_users[user_email]
                    
                    # Update user offline status
                    await ChatService.update_user_online_status(user_email, False)
                    
                    # Notify other users that this user is offline
                    await self.sio.emit('user_offline', {'email': user_email}, skip_sid=sid)
                    
                    logger.info(f"User {user_email} disconnected")
                
            except Exception as e:
                logger.error(f"Disconnection error: {e}")
        
        @self.sio.event
        async def send_message(sid, data):
            """Handle sending a message"""
            try:
                # Get sender info from connected users
                sender_email = None
                for email, socket_id in connected_users.items():
                    if socket_id == sid:
                        sender_email = email
                        break
                
                if not sender_email:
                    await self.sio.emit('error', {'message': 'User not authenticated'}, room=sid)
                    return
                
                # Get sender user info
                sender_user = await ChatService.get_user_by_email(sender_email)
                if not sender_user:
                    await self.sio.emit('error', {'message': 'Sender not found'}, room=sid)
                    return
                
                # Validate message data
                message_request = MessageRequest(**data)
                
                # Create or get conversation
                conversation_id = await ChatService.create_or_get_conversation(
                    sender_email, message_request.to_email
                )
                
                # Send message
                message = await ChatService.send_message(
                    conversation_id=conversation_id,
                    sender_email=sender_email,
                    sender_name=sender_user.name,
                    message_content=message_request.message,
                    message_type=message_request.message_type,
                    reply_to=message_request.reply_to
                )
                
                # Prepare message data for broadcast
                message_data = {
                    'id': str(message.id),
                    'conversation_id': conversation_id,
                    'sender_email': sender_email,
                    'sender_name': sender_user.name,
                    'message': message_request.message,
                    'timestamp': message.timestamp.replace(tzinfo=timezone.utc).isoformat(),
                    'message_type': message_request.message_type,
                    'reply_to': message_request.reply_to
                }
                
                # Broadcast to conversation room
                await self.sio.emit('new_message', message_data, room=f"conversation:{conversation_id}")
                
                # Send notification to recipient if they're online
                recipient_socket_id = connected_users.get(message_request.to_email)
                if recipient_socket_id:
                    await self.sio.emit('message_notification', {
                        'conversation_id': conversation_id,
                        'sender_email': sender_email,
                        'sender_name': sender_user.name,
                        'message': message_request.message
                    }, room=recipient_socket_id)
                
            except Exception as e:
                logger.error(f"Send message error: {e}")
                await self.sio.emit('error', {'message': 'Failed to send message'}, room=sid)
        
        @self.sio.event
        async def join_conversation(sid, data):
            """Join a conversation room"""
            try:
                conversation_id = data.get('conversation_id')
                if conversation_id:
                    await self.sio.enter_room(sid, f"conversation:{conversation_id}")
                    await self.sio.emit('joined_conversation', {'conversation_id': conversation_id}, room=sid)
                
            except Exception as e:
                logger.error(f"Join conversation error: {e}")
        
        @self.sio.event
        async def leave_conversation(sid, data):
            """Leave a conversation room"""
            try:
                conversation_id = data.get('conversation_id')
                if conversation_id:
                    await self.sio.leave_room(sid, f"conversation:{conversation_id}")
                    await self.sio.emit('left_conversation', {'conversation_id': conversation_id}, room=sid)
                
            except Exception as e:
                logger.error(f"Leave conversation error: {e}")
        
        @self.sio.event
        async def mark_as_read(sid, data):
            """Mark conversation as read"""
            try:
                # Get user info from connected users
                user_email = None
                for email, socket_id in connected_users.items():
                    if socket_id == sid:
                        user_email = email
                        break
                
                if not user_email:
                    return
                
                conversation_id = data.get('conversation_id')
                if conversation_id:
                    await ChatService.mark_conversation_as_read(conversation_id, user_email)
                    await self.sio.emit('marked_as_read', {
                        'conversation_id': conversation_id,
                        'user_email': user_email
                    }, room=f"conversation:{conversation_id}")
                
            except Exception as e:
                logger.error(f"Mark as read error: {e}")
        
        @self.sio.event
        async def typing_start(sid, data):
            """Handle typing start event"""
            try:
                # Get user info from connected users
                user_email = None
                for email, socket_id in connected_users.items():
                    if socket_id == sid:
                        user_email = email
                        break
                
                if not user_email:
                    return
                
                conversation_id = data.get('conversation_id')
                if conversation_id:
                    await self.sio.emit('user_typing', {
                        'conversation_id': conversation_id,
                        'user_email': user_email,
                        'typing': True
                    }, room=f"conversation:{conversation_id}", skip_sid=sid)
                
            except Exception as e:
                logger.error(f"Typing start error: {e}")
        
        @self.sio.event
        async def typing_stop(sid, data):
            """Handle typing stop event"""
            try:
                # Get user info from connected users
                user_email = None
                for email, socket_id in connected_users.items():
                    if socket_id == sid:
                        user_email = email
                        break
                
                if not user_email:
                    return
                
                conversation_id = data.get('conversation_id')
                if conversation_id:
                    await self.sio.emit('user_typing', {
                        'conversation_id': conversation_id,
                        'user_email': user_email,
                        'typing': False
                    }, room=f"conversation:{conversation_id}", skip_sid=sid)
                
            except Exception as e:
                logger.error(f"Typing stop error: {e}")
        
        @self.sio.event
        async def get_online_users(sid):
            """Get list of online users"""
            try:
                online_users = list(connected_users.keys())
                await self.sio.emit('online_users', {'users': online_users}, room=sid)
                
            except Exception as e:
                logger.error(f"Get online users error: {e}")
        
        @self.sio.event
        async def get_conversations(sid):
            """Get user conversations via Socket.IO"""
            try:
                # Get user info from connected users
                user_email = None
                for email, socket_id in connected_users.items():
                    if socket_id == sid:
                        user_email = email
                        break
                
                if not user_email:
                    await self.sio.emit('error', {'message': 'User not authenticated'}, room=sid)
                    return
                
                # Get conversations
                conversations = await ChatService.get_user_conversations(user_email)
                
                # Convert to dict format for JSON serialization
                conversations_data = []
                for conv in conversations:
                    conv_data = {
                        'conversation_id': conv.conversation_id,
                        'participants': conv.participants,
                        'last_message': conv.last_message,
                        'last_message_time': conv.last_message_time.replace(tzinfo=timezone.utc).isoformat() if conv.last_message_time else None,
                        'last_message_sender': conv.last_message_sender,
                        'unread_count': conv.unread_count
                    }
                    conversations_data.append(conv_data)
                
                await self.sio.emit('conversations_list', {'conversations': conversations_data}, room=sid)
                
            except Exception as e:
                logger.error(f"Get conversations error: {e}")
                await self.sio.emit('error', {'message': 'Failed to get conversations'}, room=sid)
        
        @self.sio.event
        async def get_conversations_enriched(sid):
            """Get user conversations with full user details via Socket.IO"""
            try:
                # Get user info from connected users
                user_email = None
                for email, socket_id in connected_users.items():
                    if socket_id == sid:
                        user_email = email
                        break
                
                if not user_email:
                    await self.sio.emit('error', {'message': 'User not authenticated'}, room=sid)
                    return
                
                # Get enriched conversations
                conversations = await ChatService.get_user_conversations_enriched(user_email)
                
                # Convert to dict format for JSON serialization
                conversations_data = []
                for conv in conversations:
                    participants_data = []
                    for participant in conv.participants:
                        participants_data.append({
                            'email': participant.email,
                            'name': participant.name,
                            'profile_image': participant.profile_image,
                            'is_online': participant.is_online
                        })
                    
                    conv_data = {
                        'conversation_id': conv.conversation_id,
                        'participants': participants_data,
                        'last_message': conv.last_message,
                        'last_message_time': conv.last_message_time.replace(tzinfo=timezone.utc).isoformat() if conv.last_message_time else None,
                        'last_message_sender': conv.last_message_sender,
                        'unread_count': conv.unread_count
                    }
                    conversations_data.append(conv_data)
                
                await self.sio.emit('enriched_conversations_list', {'conversations': conversations_data}, room=sid)
                
            except Exception as e:
                logger.error(f"Get enriched conversations error: {e}")
                await self.sio.emit('error', {'message': 'Failed to get enriched conversations'}, room=sid) 