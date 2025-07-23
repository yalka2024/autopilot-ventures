"""
Web server wrapper for AutoPilot Ventures - Personal Income Generation Platform
This enables the platform to run on Google Cloud Run
"""

import os
import asyncio
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AutoPilot Ventures - Personal Income Generation Platform",
    description="Autonomous AI-powered platform for creating and operating businesses for personal income generation",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the main application
autopilot_app = None

@app.on_event("startup")
async def startup_event():
    """Initialize the AutoPilot Ventures application on startup."""
    global autopilot_app
    try:
        # Import here to avoid startup issues
        from main import AutoPilotVenturesApp
        autopilot_app = AutoPilotVenturesApp()
        logger.info("AutoPilot Ventures application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AutoPilot Ventures application: {e}")
        # Don't raise the exception to allow the server to start
        autopilot_app = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global autopilot_app
    if autopilot_app:
        try:
            # Graceful shutdown
            await graceful_shutdown(autopilot_app)
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

async def graceful_shutdown(app_instance, timeout: int = 30) -> None:
    """Graceful shutdown function."""
    try:
        logger.info("Starting graceful shutdown...")
        # Add any cleanup logic here
        logger.info("Graceful shutdown completed")
    except Exception as e:
        logger.error(f"Error during graceful shutdown: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    try:
        return JSONResponse(content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "app_initialized": autopilot_app is not None
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e), "timestamp": datetime.utcnow().isoformat()}
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with platform information."""
    return {
        "platform": "AutoPilot Ventures - Personal Income Generation Platform",
        "version": "2.0.0",
        "description": "Autonomous AI-powered platform for creating and operating businesses for personal income generation",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "app_initialized": autopilot_app is not None
    }

# Status endpoint
@app.get("/status")
async def get_status():
    """Get platform status."""
    try:
        if not autopilot_app:
            return JSONResponse(content={
                "status": "initializing",
                "message": "Application is still initializing",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Get status from the application
        status = await autopilot_app.get_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return JSONResponse(content={
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })

# Demo endpoint
@app.get("/demo")
async def demo():
    """Simple demo endpoint."""
    return {
        "message": "AutoPilot Ventures is running!",
        "timestamp": datetime.utcnow().isoformat(),
        "app_initialized": autopilot_app is not None
    }

# Metrics endpoint for Prometheus
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    try:
        # This would return Prometheus metrics
        # For now, return basic metrics
        return {
            "platform_status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "app_initialized": autopilot_app is not None
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Get port from environment variable (Cloud Run sets PORT)
    port = int(os.environ.get("PORT", 8080))
    
    logger.info(f"Starting AutoPilot Ventures web server on port {port}")
    
    # Run the web server
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    ) 