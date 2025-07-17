# 🚀 Quick Start Guide - Chat Socket Backend

Get your real-time chat backend running in **under 2 minutes** with Docker Compose!

## 📋 Prerequisites

- **Docker** and **Docker Compose** installed on your system
- **Git** (optional, for cloning)

## ⚡ Super Quick Start

### 1. Clone & Start
```bash
git clone https://github.com/studysend/studysendchat.git
cd studysendchat
docker compose up --build
```

### 2. Access Your Chat Backend
- **🌐 API Base URL**: `http://localhost:8000`
- **📚 Interactive API Docs**: `http://localhost:8000/docs`
- **❤️ Health Check**: `http://localhost:8000/health`

That's it! Your chat backend is now running with MongoDB! 🎉

---

## 🔧 What's Included

### 🐳 Docker Services
- **🍃 MongoDB 7.0**: Local database with authentication
- **🚀 Chat Backend**: FastAPI + Socket.IO server
- **🔗 Networking**: Internal Docker network for secure communication

### 🗄️ Database Setup
- **Database Name**: `study-chat`
- **MongoDB Port**: `27017` (mapped to localhost)
- **Credentials**: `admin:password123`
- **Auto-initialization**: Collections and indexes created automatically

---

## 🛠️ Development Commands

### Start Services
```bash
# Start in detached mode
docker compose up -d

# Start with logs
docker compose up

# Rebuild and start
docker compose up --build
```

### Stop Services
```bash
# Stop containers
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f chat_backend
docker compose logs -f mongodb
```

---

## 🌐 API Usage Examples

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "chat-backend"
}
```

### 2. User Authentication
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=john@example.com&name=John Doe"
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "email": "john@example.com",
    "name": "John Doe",
    "profile_image": null
  }
}
```

### 3. Get User Conversations
```bash
curl -X GET "http://localhost:8000/api/conversations" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 4. Send a Message
```bash
curl -X POST "http://localhost:8000/api/messages/send" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "jane@example.com",
    "message": "Hello from the API!",
    "message_type": "text"
  }'
```

---

## 💬 Real-time Chat Testing

### 1. Basic Socket.IO Test
Open your browser's developer console and run:

```javascript
// Connect to Socket.IO
const socket = io("http://localhost:8000", {
  auth: { token: "YOUR_JWT_TOKEN" }
});

// Listen for messages
socket.on("new_message", (data) => {
  console.log("New message:", data);
});

// Send a message
socket.emit("send_message", {
  to_email: "recipient@example.com",
  message: "Hello from Socket.IO!",
  message_type: "text"
});
```

### 2. Test with Multiple Browser Tabs
1. **Tab 1**: Login as `user1@test.com`
2. **Tab 2**: Login as `user2@test.com` 
3. **Start chatting** between the tabs in real-time!

---

## 📊 Interactive API Documentation

Visit **`http://localhost:8000/docs`** for:

- 🔍 **Interactive API Explorer**: Test all endpoints directly
- 📖 **Complete Documentation**: Request/response schemas
- 🔐 **Authentication Testing**: Built-in JWT token management
- 🎯 **Real Examples**: Copy-paste ready code samples

### Key API Endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Login/Register user |
| `GET` | `/api/users/me` | Get current user info |
| `GET` | `/api/conversations` | Get user conversations |
| `GET` | `/api/conversations/{id}/messages` | Get conversation messages |
| `POST` | `/api/messages/send` | Send message via REST |
| `GET` | `/api/users/search?query=john` | Search users |

---

## 🔧 Configuration & Environment

### Environment Variables (Already Configured)
The Docker setup includes these pre-configured environment variables:

```yaml
MONGODB_URL: mongodb://admin:password123@mongodb:27017/study-chat?authSource=admin
DATABASE_NAME: study-chat
JWT_SECRET_KEY: your-production-secret-key-change-this-in-production
JWT_ALGORITHM: HS256
JWT_EXPIRE_MINUTES: 1440
CORS_ORIGINS: http://localhost:3000,http://localhost:8080,http://localhost:5173
```

### For Production
1. **Change JWT Secret**: Update `JWT_SECRET_KEY` in `docker-compose.yml`
2. **Update CORS Origins**: Add your domain to `CORS_ORIGINS`
3. **MongoDB Security**: Use strong passwords and enable SSL

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 🔴 Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Use different ports
docker compose -f docker-compose.yml up --build
```

#### 🔴 MongoDB Connection Issues
```bash
# Check MongoDB logs
docker compose logs mongodb

# Restart MongoDB
docker compose restart mongodb
```

#### 🔴 Permission Errors
```bash
# Fix permissions (Linux/Mac)
sudo chown -R $USER:$USER .

# Or run with sudo
sudo docker compose up --build
```

#### 🔴 Build Errors
```bash
# Clean build
docker compose down -v
docker system prune
docker compose up --build
```

---

## 🚀 Integration with Your App

### Frontend Integration
```javascript
// React/Vue/Angular example
import io from 'socket.io-client';

const socket = io('http://localhost:8000', {
  auth: { token: localStorage.getItem('jwt_token') }
});

socket.on('new_message', (message) => {
  // Handle incoming messages
  updateChatUI(message);
});
```

### Backend Integration
```python
# Python client example
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login', {
    'email': 'user@example.com',
    'name': 'User Name'
})
token = response.json()['access_token']

# Send message
requests.post('http://localhost:8000/api/messages/send', 
    headers={'Authorization': f'Bearer {token}'},
    json={
        'to_email': 'recipient@example.com',
        'message': 'Hello from Python!',
        'message_type': 'text'
    }
)
```

---

## 📈 Next Steps

### 🔧 Customization
- **Authentication**: Integrate with your existing user system in `routes.py`
- **Database**: Sync users from your PostgreSQL to MongoDB  
- **Features**: Add file uploads, group chats, message encryption

### 🚀 Deployment
- **Production**: Use Docker Swarm or Kubernetes
- **Scaling**: Add Redis for Socket.IO clustering
- **Monitoring**: Integrate with your logging/monitoring stack

### 🎯 Advanced Features
- **Push Notifications**: Integrate with FCM/APNS
- **File Sharing**: Add file upload endpoints
- **Voice/Video**: Integrate WebRTC for calls
- **Bot Integration**: Add AI chatbot support

---

## 🆘 Need Help?

### 📝 Logs
```bash
# Application logs
docker compose logs -f chat_backend

# Database logs
docker compose logs -f mongodb

# All logs with timestamps
docker compose logs -f --timestamps
```

### 🔍 Debug Mode
For detailed debugging, modify `docker-compose.yml`:
```yaml
command: ["python", "run.py", "--reload"]  # Development mode
```

### 🌐 Resources
- **📚 Full API Documentation**: `/docs` endpoint
- **🔧 Configuration**: Check `config.py` and `docker-compose.yml`
- **🗄️ Database**: MongoDB collections auto-created on first use

---

**🎉 Happy Chatting!** Your real-time chat backend is now ready for production use! 