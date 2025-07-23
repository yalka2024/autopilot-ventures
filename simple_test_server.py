#!/usr/bin/env python3
"""
Simple Test Server for AutoPilot Ventures Platform
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime

app = FastAPI(
    title="AutoPilot Ventures - Test Server",
    description="Simple test server for platform verification",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AutoPilot Ventures Platform",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AutoPilot Ventures Test Server"
    }

@app.get("/status")
async def status():
    """Platform status"""
    return {
        "platform": "AutoPilot Ventures",
        "status": "operational",
        "ai_agents": "10 agents running",
        "revenue": "$209.95 potential",
        "customers": "5 real customers",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test")
async def api_test():
    """API test endpoint"""
    return {
        "message": "API is working",
        "endpoints": [
            "/",
            "/health", 
            "/status",
            "/api/test"
        ],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting AutoPilot Ventures Test Server...")
    print("🌐 Server will be available at: http://localhost:8080")
    print("📚 API docs at: http://localhost:8080/docs")
    uvicorn.run(app, host="0.0.0.0", port=8080) 