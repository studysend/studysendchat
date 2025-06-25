# 🚀 Quick Start Guide - Chat Socket Backend

Get your real-time chat backend running in under 5 minutes!

## 📋 Prerequisites

- Python 3.8+ installed
- MongoDB running (local or cloud)
- Git (optional)

## ⚡ Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Edit the `.env` file or set environment variables:
```bash
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=chat_app
JWT_SECRET_KEY=your-secret-key-here
```

### 3. Test Setup (Optional but Recommended)
```bash
python test_setup.py
```

### 4. Start the Server
```bash
# Development mode with auto-reload
python run.py --reload

# Or simply
python main.py
```

### 5. Test the Chat
Open `client_example.html` in two browser tabs and start chatting!

## 🎯 Quick Demo

1. **Open the client**: Open `client_example.html` in your browser
2. **Login**: Use any email and name (e.g., `user1@test.com`, `John`)
3. **Open another tab**: Open the same HTML file again
4. **Login as another user**: Use different email (e.g., `user2@test.com`, `Jane`)
5. **Start chatting**: Send messages between the two tabs!

## 🔗 API Endpoints

Once running on `http://localhost:8000`:

- **Health Check**: `GET /health`
- **API Docs**: `GET /docs` (Swagger UI)
- **Login**: `POST /api/auth/login`
- **Get Conversations**: `GET /api/conversations`
- **Send Message**: `POST /api/messages/send`

## 🐳 Docker Quick Start

```bash
# Start everything with Docker
docker-compose up

# The app will be available at http://localhost:8000
# MongoDB Express at http://localhost:8081 (admin/password123)
```

## 🔧 Development Tips

1. **Use auto-reload** for development:
   ```bash
   python run.py --reload
   ```

2. **Check logs** for debugging:
   ```bash
   python main.py
   ```

3. **Test with multiple clients**:
   - Open `client_example.html` in multiple browser tabs
   - Or use different browsers
   - Or use incognito mode

## 🌐 Integration with Your App

To integrate with your existing PostgreSQL application:

1. **Modify authentication** in `routes.py` to use your user system
2. **Sync user data** from your PostgreSQL to MongoDB
3. **Add chat endpoints** to your existing API
4. **Include the Socket.IO client** in your frontend

## 🎮 Next Steps

- Customize the authentication in `routes.py`
- Add file upload support for images/documents
- Implement group chats
- Add message encryption
- Set up push notifications
- Deploy to production

## 📞 Support

If something doesn't work:

1. Check the console for error messages
2. Ensure MongoDB is running
3. Verify all dependencies are installed
4. Run the test script: `python test_setup.py`

Happy chatting! 🎉 