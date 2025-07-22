#!/usr/bin/env python3
"""
Health Server for AutoPilot Ventures
Simple FastAPI server for container health monitoring.
"""

import os
import logging
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoPilot Ventures Health Server",
    description="Health monitoring server for AutoPilot Ventures containers",
    version="1.0.0"
)

# Startup time for uptime calculation
startup_time = datetime.utcnow()

@app.on_event("startup")
async def startup_event():
    """Log startup event."""
    logger.info("🚀 AutoPilot Ventures Health Server starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    logger.info(f"Autonomy Level: {os.getenv('AUTONOMY_LEVEL', 'unknown')}")
    logger.info(f"Phase 3 Enabled: {os.getenv('PHASE3_ENABLED', 'false')}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AutoPilot Ventures Health Server",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - startup_time).total_seconds()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for container health monitoring."""
    try:
        # Basic health check
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - startup_time).total_seconds(),
            "environment": os.getenv('ENVIRONMENT', 'unknown'),
            "autonomy_level": os.getenv('AUTONOMY_LEVEL', 'unknown'),
            "phase3_enabled": os.getenv('PHASE3_ENABLED', 'false'),
            "vector_memory_enabled": os.getenv('VECTOR_MEMORY_ENABLED', 'false'),
            "self_tuning_enabled": os.getenv('SELF_TUNING_ENABLED', 'false'),
            "reinforcement_learning_enabled": os.getenv('REINFORCEMENT_LEARNING_ENABLED', 'false'),
            "autonomous_workflow_enabled": os.getenv('AUTONOMOUS_WORKFLOW_ENABLED', 'false')
        }
        
        logger.info("✅ Health check passed")
        return JSONResponse(content=health_status, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/status")
async def status_check():
    """Detailed status endpoint."""
    try:
        status = {
            "service": "AutoPilot Ventures Health Server",
            "version": "1.0.0",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - startup_time).total_seconds(),
            "environment": {
                "ENVIRONMENT": os.getenv('ENVIRONMENT', 'unknown'),
                "AUTONOMY_LEVEL": os.getenv('AUTONOMY_LEVEL', 'unknown'),
                "BUDGET_THRESHOLD": os.getenv('BUDGET_THRESHOLD', 'unknown'),
                "PHASE3_ENABLED": os.getenv('PHASE3_ENABLED', 'false'),
                "VECTOR_MEMORY_ENABLED": os.getenv('VECTOR_MEMORY_ENABLED', 'false'),
                "SELF_TUNING_ENABLED": os.getenv('SELF_TUNING_ENABLED', 'false'),
                "REINFORCEMENT_LEARNING_ENABLED": os.getenv('REINFORCEMENT_LEARNING_ENABLED', 'false'),
                "AUTONOMOUS_WORKFLOW_ENABLED": os.getenv('AUTONOMOUS_WORKFLOW_ENABLED', 'false')
            },
            "features": {
                "vector_memory": os.getenv('VECTOR_MEMORY_ENABLED', 'false') == 'true',
                "self_tuning": os.getenv('SELF_TUNING_ENABLED', 'false') == 'true',
                "reinforcement_learning": os.getenv('REINFORCEMENT_LEARNING_ENABLED', 'false') == 'true',
                "autonomous_workflow": os.getenv('AUTONOMOUS_WORKFLOW_ENABLED', 'false') == 'true',
                "phase3_intelligence": os.getenv('PHASE3_ENABLED', 'false') == 'true'
            }
        }
        
        logger.info("📊 Status check completed")
        return JSONResponse(content=status, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Simulate readiness check
        readiness_status = {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "AutoPilot Ventures is ready to process requests"
        }
        
        logger.info("✅ Readiness check passed")
        return JSONResponse(content=readiness_status, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@app.get("/live")
async def liveness_check():
    """Liveness check endpoint."""
    try:
        liveness_status = {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - startup_time).total_seconds()
        }
        
        logger.info("💓 Liveness check passed")
        return JSONResponse(content=liveness_status, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Liveness check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service not alive: {str(e)}")

if __name__ == "__main__":
    logger.info("🚀 Starting AutoPilot Ventures Health Server...")
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    
    logger.info(f"🌐 Server will run on {host}:{port}")
    logger.info("📋 Available endpoints:")
    logger.info("  - GET /health - Health check for container monitoring")
    logger.info("  - GET /status - Detailed service status")
    logger.info("  - GET /ready - Readiness check")
    logger.info("  - GET /live - Liveness check")
    logger.info("  - GET / - Root endpoint")
    
    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    ) 