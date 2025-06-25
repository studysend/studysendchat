import uvicorn
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from database import connect_to_mongo, close_mongo_connection
from socket_handlers import SocketHandler
from config import settings
import routes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.CORS_ORIGINS,
    logger=True,
    engineio_logger=True
)

# Create FastAPI app
app = FastAPI(
    title="Chat Socket Backend",
    description="Real-time chat backend using FastAPI and Socket.IO with MongoDB",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize Socket.IO handlers
socket_handler = SocketHandler(sio)

# Include API routes
app.include_router(routes.router, prefix="/api")

# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await connect_to_mongo()
    logger.info("Chat backend started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_mongo_connection()
    logger.info("Chat backend shutdown")

@app.get("/")
async def root():
    return {"message": "Chat Socket Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chat-backend"}

if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 