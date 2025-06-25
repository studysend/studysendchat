#!/usr/bin/env python3
"""
Startup script for Chat Socket Backend
"""
import os
import sys
import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(description='Chat Socket Backend Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    parser.add_argument('--production', action='store_true', help='Run in production mode')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    
    args = parser.parse_args()
    
    # Determine the app to run
    app_module = "main:socket_app"
    
    # Set log level
    log_level = "info" if args.production else "debug"
    
    if args.production:
        print(f"🚀 Starting Chat Backend in PRODUCTION mode on {args.host}:{args.port}")
        print(f"   Workers: {args.workers}")
        uvicorn.run(
            app_module,
            host=args.host,
            port=args.port,
            workers=args.workers,
            log_level=log_level,
            access_log=True
        )
    else:
        print(f"🛠️ Starting Chat Backend in DEVELOPMENT mode on {args.host}:{args.port}")
        print(f"   Auto-reload: {args.reload}")
        uvicorn.run(
            app_module,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=log_level,
            access_log=True
        )

if __name__ == "__main__":
    main() 