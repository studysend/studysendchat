// MongoDB initialization script
db = db.getSiblingDB('chat_app');

// Create collections
db.createCollection('users');
db.createCollection('conversations');
db.createCollection('chat_messages');

// Create indexes for better performance
db.chat_messages.createIndex({ "conversation_id": 1, "timestamp": -1 });
db.conversations.createIndex({ "participants": 1 });
db.conversations.createIndex({ "last_message_time": -1 });
db.users.createIndex({ "email": 1 }, { unique: true });

print('Chat application database initialized successfully!'); 