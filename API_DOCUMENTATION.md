# 📚 Chat Socket Backend API Documentation

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [REST API Endpoints](#rest-api-endpoints)
- [Socket.IO Events](#socketio-events)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Integration Examples](#integration-examples)
- [Postman Collection](#postman-collection)

## Overview

The Chat Socket Backend provides both REST API endpoints and real-time Socket.IO communication for chat functionality. The API uses JWT tokens for authentication and MongoDB for data persistence.

**Base URL:** `http://localhost:8000`  
**API Prefix:** `/api`  
**Socket.IO Namespace:** `/` (default)

## Authentication

### JWT Token Authentication

All protected endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```

### Token Acquisition

Tokens are obtained through the login endpoint and are valid for 24 hours by default.

---

# REST API Endpoints

## Authentication Endpoints

### Login/Register User

Creates a new user or logs in an existing user and returns a JWT token.

**Endpoint:** `POST /api/auth/login`

**Request:**
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

email=user@example.com&name=John+Doe&profile_image=https://example.com/profile.jpg
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "email": "user@example.com",
    "name": "John Doe",
    "profile_image": "https://example.com/profile.jpg"
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Login failed

---

## User Endpoints

### Get Current User Info

Retrieves information about the authenticated user.

**Endpoint:** `GET /api/users/me`

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "profile_image": "https://example.com/profile.jpg",
  "is_online": true,
  "last_seen": "2023-12-07T10:30:00.000Z"
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - User not found
- `500 Internal Server Error` - Server error

### Search Users

Search for users by email or name.

**Endpoint:** `GET /api/users/search`

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `query` (required) - Search term to match against email or name

**Example:**
```http
GET /api/users/search?query=john
```

**Response:**
```json
[
  {
    "email": "john.doe@example.com",
    "name": "John Doe",
    "profile_image": "https://example.com/profile.jpg",
    "is_online": true
  },
  {
    "email": "johnny@example.com",
    "name": "Johnny Smith",
    "profile_image": null,
    "is_online": false
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token
- `500 Internal Server Error` - Search failed

---

## Conversation Endpoints

### Get User Conversations

Retrieves all conversations for the authenticated user, ordered by last message time.

**Endpoint:** `GET /api/conversations`

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response:**
```json
[
  {
    "conversation_id": "64f1234567890abcdef12345",
    "participants": ["user@example.com", "other@example.com"],
    "last_message": "Hello there!",
    "last_message_time": "2023-12-07T10:30:00.000Z",
    "last_message_sender": "other@example.com",
    "unread_count": 3
  },
  {
    "conversation_id": "64f1234567890abcdef12346",
    "participants": ["user@example.com", "another@example.com"],
    "last_message": "How are you?",
    "last_message_time": "2023-12-07T09:15:00.000Z",
    "last_message_sender": "user@example.com",
    "unread_count": 0
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token
- `500 Internal Server Error` - Failed to get conversations

### Start New Conversation

Creates a new conversation with another user or returns existing conversation.

**Endpoint:** `POST /api/conversations/start`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/x-www-form-urlencoded
```

**Request:**
```http
POST /api/conversations/start
Content-Type: application/x-www-form-urlencoded

to_email=other@example.com
```

**Response:**
```json
{
  "conversation_id": "64f1234567890abcdef12345",
  "participants": ["user@example.com", "other@example.com"]
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Target user not found
- `500 Internal Server Error` - Failed to start conversation

### Get Conversation Messages

Retrieves messages from a specific conversation with pagination.

**Endpoint:** `GET /api/conversations/{conversation_id}/messages`

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of messages to skip
- `limit` (optional, default: 50) - Maximum number of messages to return

**Example:**
```http
GET /api/conversations/64f1234567890abcdef12345/messages?skip=0&limit=20
```

**Response:**
```json
[
  {
    "id": "64f1234567890abcdef12347",
    "conversation_id": "64f1234567890abcdef12345",
    "sender_email": "other@example.com",
    "sender_name": "Jane Doe",
    "message": "Hello there!",
    "timestamp": "2023-12-07T10:30:00.000Z",
    "message_type": "text",
    "edited": false,
    "reply_to": null
  },
  {
    "id": "64f1234567890abcdef12348",
    "conversation_id": "64f1234567890abcdef12345",
    "sender_email": "user@example.com",
    "sender_name": "John Doe",
    "message": "Hi! How are you?",
    "timestamp": "2023-12-07T10:32:00.000Z",
    "message_type": "text",
    "edited": false,
    "reply_to": "64f1234567890abcdef12347"
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token
- `500 Internal Server Error` - Failed to get messages

### Mark Conversation as Read

Marks all messages in a conversation as read for the current user.

**Endpoint:** `POST /api/conversations/{conversation_id}/mark-read`

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "message": "Conversation marked as read"
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token
- `500 Internal Server Error` - Failed to mark as read

---

## Message Endpoints

### Send Message (REST)

Sends a message via REST API (alternative to Socket.IO).

**Endpoint:** `POST /api/messages/send`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request:**
```json
{
  "to_email": "recipient@example.com",
  "message": "Hello there!",
  "message_type": "text",
  "reply_to": "64f1234567890abcdef12347"
}
```

**Response:**
```json
{
  "id": "64f1234567890abcdef12349",
  "conversation_id": "64f1234567890abcdef12345",
  "sender_email": "user@example.com",
  "sender_name": "John Doe",
  "message": "Hello there!",
  "timestamp": "2023-12-07T10:35:00.000Z",
  "message_type": "text",
  "reply_to": "64f1234567890abcdef12347"
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Recipient not found
- `500 Internal Server Error` - Failed to send message

---

# Socket.IO Events

## Connection

### Establishing Connection

Connect to the Socket.IO server with JWT authentication:

```javascript
const socket = io("http://localhost:8000", {
  auth: {
    token: "your-jwt-token-here"
  }
});
```

### Connection Events

**Server Response Events:**
- `connect` - Successfully connected
- `disconnect` - Disconnected from server
- `connect_error` - Connection failed

---

## Client to Server Events

### Send Message

Send a real-time message to another user.

**Event:** `send_message`

**Data:**
```javascript
socket.emit("send_message", {
  to_email: "recipient@example.com",
  message: "Hello there!",
  message_type: "text",  // "text", "image", "file"
  reply_to: "message_id_here"  // optional
});
```

### Join Conversation

Join a conversation room to receive real-time updates.

**Event:** `join_conversation`

**Data:**
```javascript
socket.emit("join_conversation", {
  conversation_id: "64f1234567890abcdef12345"
});
```

### Leave Conversation

Leave a conversation room.

**Event:** `leave_conversation`

**Data:**
```javascript
socket.emit("leave_conversation", {
  conversation_id: "64f1234567890abcdef12345"
});
```

### Mark as Read

Mark messages in a conversation as read.

**Event:** `mark_as_read`

**Data:**
```javascript
socket.emit("mark_as_read", {
  conversation_id: "64f1234567890abcdef12345"
});
```

### Typing Indicators

Notify other users when you're typing.

**Events:** `typing_start`, `typing_stop`

**Data:**
```javascript
// Start typing
socket.emit("typing_start", {
  conversation_id: "64f1234567890abcdef12345"
});

// Stop typing
socket.emit("typing_stop", {
  conversation_id: "64f1234567890abcdef12345"
});
```

### Get Online Users

Request list of currently online users.

**Event:** `get_online_users`

**Data:**
```javascript
socket.emit("get_online_users");
```

---

## Server to Client Events

### New Message

Receive a new message in real-time.

**Event:** `new_message`

**Data:**
```javascript
socket.on("new_message", (data) => {
  console.log(data);
  /*
  {
    "id": "64f1234567890abcdef12349",
    "conversation_id": "64f1234567890abcdef12345",
    "sender_email": "sender@example.com",
    "sender_name": "Jane Doe",
    "message": "Hello there!",
    "timestamp": "2023-12-07T10:35:00.000Z",
    "message_type": "text",
    "reply_to": null
  }
  */
});
```

### Message Notification

Receive notification for new messages (useful for notifications).

**Event:** `message_notification`

**Data:**
```javascript
socket.on("message_notification", (data) => {
  console.log(data);
  /*
  {
    "conversation_id": "64f1234567890abcdef12345",
    "sender_email": "sender@example.com",
    "sender_name": "Jane Doe",
    "message": "Hello there!"
  }
  */
});
```

### User Status Updates

Receive notifications when users come online or go offline.

**Events:** `user_online`, `user_offline`

**Data:**
```javascript
socket.on("user_online", (data) => {
  console.log(`${data.email} came online`);
});

socket.on("user_offline", (data) => {
  console.log(`${data.email} went offline`);
});
```

### Typing Indicators

Receive typing status updates from other users.

**Event:** `user_typing`

**Data:**
```javascript
socket.on("user_typing", (data) => {
  console.log(data);
  /*
  {
    "conversation_id": "64f1234567890abcdef12345",
    "user_email": "user@example.com",
    "typing": true  // or false
  }
  */
});
```

### Online Users List

Receive list of currently online users.

**Event:** `online_users`

**Data:**
```javascript
socket.on("online_users", (data) => {
  console.log(data);
  /*
  {
    "users": ["user1@example.com", "user2@example.com"]
  }
  */
});
```

### Read Status Updates

Receive notifications when messages are marked as read.

**Event:** `marked_as_read`

**Data:**
```javascript
socket.on("marked_as_read", (data) => {
  console.log(data);
  /*
  {
    "conversation_id": "64f1234567890abcdef12345",
    "user_email": "user@example.com"
  }
  */
});
```

### Connection Status

Handle connection confirmations for room operations.

**Events:** `joined_conversation`, `left_conversation`

**Data:**
```javascript
socket.on("joined_conversation", (data) => {
  console.log(`Joined conversation: ${data.conversation_id}`);
});

socket.on("left_conversation", (data) => {
  console.log(`Left conversation: ${data.conversation_id}`);
});
```

### Error Handling

Handle Socket.IO errors.

**Event:** `error`

**Data:**
```javascript
socket.on("error", (data) => {
  console.error("Socket error:", data.message);
});
```

---

# Error Handling

## HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Error Response Format

```json
{
  "detail": "Error message description"
}
```

## Common Socket.IO Errors

- `User not authenticated` - Invalid JWT token
- `Failed to send message` - Message sending failed
- `Sender not found` - User not found in database

---

# Rate Limiting

Currently, there are no rate limits implemented. In production, consider implementing:

- **Message sending**: 100 messages per minute per user
- **API requests**: 1000 requests per hour per IP
- **Connection attempts**: 10 per minute per IP

---

# Integration Examples

## React/JavaScript Integration

### Setting up Socket.IO Client

```javascript
import io from 'socket.io-client';

class ChatService {
  constructor(token) {
    this.socket = io('http://localhost:8000', {
      auth: { token }
    });
    
    this.setupEventListeners();
  }
  
  setupEventListeners() {
    this.socket.on('connect', () => {
      console.log('Connected to chat server');
    });
    
    this.socket.on('new_message', (message) => {
      // Handle new message
      this.handleNewMessage(message);
    });
    
    this.socket.on('user_typing', (data) => {
      // Handle typing indicator
      this.handleTypingIndicator(data);
    });
  }
  
  sendMessage(toEmail, message) {
    this.socket.emit('send_message', {
      to_email: toEmail,
      message: message,
      message_type: 'text'
    });
  }
  
  joinConversation(conversationId) {
    this.socket.emit('join_conversation', {
      conversation_id: conversationId
    });
  }
  
  startTyping(conversationId) {
    this.socket.emit('typing_start', {
      conversation_id: conversationId
    });
  }
  
  stopTyping(conversationId) {
    this.socket.emit('typing_stop', {
      conversation_id: conversationId
    });
  }
}
```

### REST API Integration

```javascript
class ChatAPI {
  constructor(token) {
    this.baseURL = 'http://localhost:8000/api';
    this.token = token;
  }
  
  async getConversations() {
    const response = await fetch(`${this.baseURL}/conversations`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    return response.json();
  }
  
  async getMessages(conversationId, skip = 0, limit = 50) {
    const response = await fetch(
      `${this.baseURL}/conversations/${conversationId}/messages?skip=${skip}&limit=${limit}`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      }
    );
    return response.json();
  }
  
  async sendMessage(toEmail, message) {
    const response = await fetch(`${this.baseURL}/messages/send`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        to_email: toEmail,
        message: message,
        message_type: 'text'
      })
    });
    return response.json();
  }
  
  async searchUsers(query) {
    const response = await fetch(
      `${this.baseURL}/users/search?query=${encodeURIComponent(query)}`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      }
    );
    return response.json();
  }
}
```

## Python Client Example

```python
import socketio
import requests

class ChatClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.sio = socketio.Client()
        
    def login(self, email, name):
        response = requests.post(f"{self.api_url}/auth/login", {
            'email': email,
            'name': name
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']
            return True
        return False
    
    def connect_socket(self):
        self.sio.connect(self.base_url, auth={'token': self.token})
        
        @self.sio.on('new_message')
        def on_new_message(data):
            print(f"New message: {data['message']} from {data['sender_name']}")
            
        @self.sio.on('user_online')
        def on_user_online(data):
            print(f"User {data['email']} came online")
    
    def send_message(self, to_email, message):
        self.sio.emit('send_message', {
            'to_email': to_email,
            'message': message,
            'message_type': 'text'
        })
    
    def get_conversations(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f"{self.api_url}/conversations", headers=headers)
        return response.json() if response.status_code == 200 else None
```

---

# Postman Collection

You can import this Postman collection to test all API endpoints:

```json
{
  "info": {
    "name": "Chat Socket Backend API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{jwt_token}}",
        "type": "string"
      }
    ]
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "jwt_token",
      "value": ""
    }
  ],
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [],
            "body": {
              "mode": "urlencoded",
              "urlencoded": [
                {
                  "key": "email",
                  "value": "test@example.com"
                },
                {
                  "key": "name",
                  "value": "Test User"
                }
              ]
            },
            "url": "{{base_url}}/api/auth/login"
          }
        }
      ]
    },
    {
      "name": "Users",
      "item": [
        {
          "name": "Get Current User",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/api/users/me"
          }
        },
        {
          "name": "Search Users",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/api/users/search?query=test"
          }
        }
      ]
    },
    {
      "name": "Conversations",
      "item": [
        {
          "name": "Get Conversations",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/api/conversations"
          }
        },
        {
          "name": "Start Conversation",
          "request": {
            "method": "POST",
            "body": {
              "mode": "urlencoded",
              "urlencoded": [
                {
                  "key": "to_email",
                  "value": "other@example.com"
                }
              ]
            },
            "url": "{{base_url}}/api/conversations/start"
          }
        }
      ]
    }
  ]
}
```

---

# Additional Resources

- **Interactive API Docs**: Visit `http://localhost:8000/docs` when the server is running
- **Health Check**: `GET http://localhost:8000/health`
- **Socket.IO Test Page**: Open `client_example.html` in your browser

For more detailed examples and integration guides, see the [README.md](README.md) and [QUICK_START.md](QUICK_START.md) files. 