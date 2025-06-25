# Chat Socket Backend

A real-time chat backend built with FastAPI and Socket.IO, using MongoDB for data storage. This backend provides both REST API endpoints and real-time Socket.IO communication for chat functionality.

## Features

- ✅ Real-time messaging with Socket.IO
- ✅ REST API for chat operations
- ✅ User authentication with JWT
- ✅ MongoDB integration for message and conversation storage
- ✅ Online/offline user status tracking
- ✅ Typing indicators
- ✅ Message read status
- ✅ Conversation management
- ✅ User search functionality
- ✅ CORS support for web clients

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Socket.IO** - Real-time bidirectional communication
- **MongoDB** - Document database for storing messages and conversations
- **Motor** - Async MongoDB driver
- **JWT** - JSON Web Tokens for authentication
- **Pydantic** - Data validation and serialization

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud instance)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chat-socket-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory and configure the following:
   ```bash
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=chat_app
   JWT_SECRET_KEY=your-secret-key-here-change-in-production
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_MINUTES=1440
   CORS_ORIGINS=http://localhost:3000,http://localhost:8080
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

The server will start on `http://localhost:8000`

## API Documentation

### Authentication

#### Login/Register
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "profile_image": "https://example.com/profile.jpg"
}
```

Response:
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

### User Operations

#### Get Current User Info
```http
GET /api/users/me
Authorization: Bearer <token>
```

#### Search Users
```http
GET /api/users/search?query=john
Authorization: Bearer <token>
```

### Conversations

#### Get User Conversations
```http
GET /api/conversations
Authorization: Bearer <token>
```

#### Start New Conversation
```http
POST /api/conversations/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "to_email": "other@example.com"
}
```

#### Get Conversation Messages
```http
GET /api/conversations/{conversation_id}/messages?skip=0&limit=50
Authorization: Bearer <token>
```

#### Mark Conversation as Read
```http
POST /api/conversations/{conversation_id}/mark-read
Authorization: Bearer <token>
```

### Messages

#### Send Message (REST)
```http
POST /api/messages/send
Authorization: Bearer <token>
Content-Type: application/json

{
  "to_email": "recipient@example.com",
  "message": "Hello there!",
  "message_type": "text",
  "reply_to": null
}
```

## Socket.IO Events

### Client to Server Events

#### Connection
```javascript
const socket = io("http://localhost:8000", {
  auth: {
    token: "your-jwt-token-here"
  }
});
```

#### Send Message
```javascript
socket.emit("send_message", {
  to_email: "recipient@example.com",
  message: "Hello!",
  message_type: "text",
  reply_to: null
});
```

#### Join Conversation
```javascript
socket.emit("join_conversation", {
  conversation_id: "conversation_id_here"
});
```

#### Leave Conversation
```javascript
socket.emit("leave_conversation", {
  conversation_id: "conversation_id_here"
});
```

#### Mark as Read
```javascript
socket.emit("mark_as_read", {
  conversation_id: "conversation_id_here"
});
```

#### Typing Indicators
```javascript
// Start typing
socket.emit("typing_start", {
  conversation_id: "conversation_id_here"
});

// Stop typing
socket.emit("typing_stop", {
  conversation_id: "conversation_id_here"
});
```

#### Get Online Users
```javascript
socket.emit("get_online_users");
```

### Server to Client Events

#### New Message
```javascript
socket.on("new_message", (data) => {
  console.log("New message:", data);
  // data contains: id, conversation_id, sender_email, sender_name, message, timestamp, etc.
});
```

#### Message Notification
```javascript
socket.on("message_notification", (data) => {
  console.log("Message notification:", data);
  // Show notification for new message
});
```

#### User Status
```javascript
socket.on("user_online", (data) => {
  console.log("User came online:", data.email);
});

socket.on("user_offline", (data) => {
  console.log("User went offline:", data.email);
});
```

#### Typing Indicators
```javascript
socket.on("user_typing", (data) => {
  console.log(`${data.user_email} is ${data.typing ? 'typing' : 'not typing'}`);
});
```

#### Online Users List
```javascript
socket.on("online_users", (data) => {
  console.log("Online users:", data.users);
});
```

#### Read Status
```javascript
socket.on("marked_as_read", (data) => {
  console.log("Conversation marked as read:", data);
});
```

#### Errors
```javascript
socket.on("error", (data) => {
  console.error("Socket error:", data.message);
});
```

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "email": "string",
  "name": "string",
  "profile_image": "string",
  "is_online": "boolean",
  "last_seen": "datetime",
  "socket_id": "string"
}
```

### Conversations Collection
```json
{
  "_id": "ObjectId",
  "participants": ["email1", "email2"],
  "conversation_type": "direct",
  "created_at": "datetime",
  "last_message": "string",
  "last_message_time": "datetime",
  "last_message_sender": "string",
  "unread_count": {
    "email1": 0,
    "email2": 5
  }
}
```

### Chat Messages Collection
```json
{
  "_id": "ObjectId",
  "conversation_id": "string",
  "sender_email": "string",
  "sender_name": "string",
  "message": "string",
  "timestamp": "datetime",
  "message_type": "text",
  "edited": false,
  "edited_at": null,
  "reply_to": "message_id"
}
```

## Integration with Existing System

To integrate this chat system with your existing PostgreSQL-based application:

1. **User Authentication**: Modify the `/api/auth/login` endpoint to validate users against your existing `credentials` and `profile` tables.

2. **User Data Sync**: Create a service to sync user data from PostgreSQL to MongoDB when users first access the chat system.

3. **Notifications**: Integrate with your existing `notifications` table to store chat notifications.

4. **Profile Integration**: Use profile data from your `profile` table for user names and images.

## Development

### Running in Development Mode
```bash
python main.py
```

The server will start with auto-reload enabled on `http://localhost:8000`

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

### Monitoring
- Health check endpoint: `http://localhost:8000/health`
- Root endpoint: `http://localhost:8000/`

## Deployment

### Environment Variables for Production
```bash
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database
DATABASE_NAME=chat_app_prod
JWT_SECRET_KEY=very-secure-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Docker Deployment
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## License

This project is licensed under the MIT License. 