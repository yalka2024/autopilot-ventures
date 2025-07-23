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

# Import the main application
from main import AutoPilotVenturesApp

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
        autopilot_app = AutoPilotVenturesApp()
        logger.info("AutoPilot Ventures application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AutoPilot Ventures application: {e}")
        raise

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

async def graceful_shutdown(app_instance: AutoPilotVenturesApp, timeout: int = 30) -> None:
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
        if not autopilot_app:
            raise HTTPException(status_code=503, detail="Application not initialized")
        
        health_status = await autopilot_app.health_check()
        return JSONResponse(content=health_status)
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
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "create_business": "/business/create",
            "run_workflow": "/workflow/run",
            "run_agent": "/agent/run"
        }
    }

# Platform status endpoint
@app.get("/status")
async def get_status():
    """Get platform status."""
    try:
        if not autopilot_app:
            raise HTTPException(status_code=503, detail="Application not initialized")
        
        status = autopilot_app.get_platform_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Create business endpoint
@app.post("/business/create")
async def create_business(
    name: str,
    description: str,
    niche: str,
    language: str = "en"
):
    """Create a new business for personal income generation."""
    try:
        if not autopilot_app:
            raise HTTPException(status_code=503, detail="Application not initialized")
        
        result = await autopilot_app.create_business(name, description, niche, language)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Business creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run workflow endpoint
@app.post("/workflow/run")
async def run_workflow(workflow_config: Dict[str, Any], language: str = "en"):
    """Run a complete workflow with all agents."""
    try:
        if not autopilot_app:
            raise HTTPException(status_code=503, detail="Application not initialized")
        
        result = await autopilot_app.run_workflow(workflow_config, language)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run single agent endpoint
@app.post("/agent/run")
async def run_agent(agent_type: str, config: Dict[str, Any]):
    """Run a single agent."""
    try:
        if not autopilot_app:
            raise HTTPException(status_code=503, detail="Application not initialized")
        
        result = await autopilot_app.run_single_agent(agent_type, **config)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Multilingual demo endpoint
@app.get("/demo/{language}")
async def multilingual_demo(language: str):
    """Run multilingual demonstration."""
    try:
        if not autopilot_app:
            raise HTTPException(status_code=503, detail="Application not initialized")
        
        result = await autopilot_app.multilingual_demo(language)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Multilingual demo failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Master agent status endpoint
@app.get("/master/status")
async def master_status():
    """Get master agent status."""
    try:
        if not autopilot_app or not autopilot_app.master_agent:
            raise HTTPException(status_code=503, detail="Master agent not available")
        
        status = autopilot_app.master_agent.get_master_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Master status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Income report endpoint
@app.get("/income/report")
async def income_report():
    """Generate income projection report."""
    try:
        if not autopilot_app or not autopilot_app.master_agent:
            raise HTTPException(status_code=503, detail="Master agent not available")
        
        income_summary = autopilot_app.master_agent.get_income_summary()
        return JSONResponse(content=income_summary)
    except Exception as e:
        logger.error(f"Income report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Start autonomous operation endpoint
@app.post("/autonomous/start")
async def start_autonomous(background_tasks: BackgroundTasks, autonomy_mode: str = "semi"):
    """Start autonomous operation mode."""
    try:
        if not autopilot_app or not autopilot_app.master_agent:
            raise HTTPException(status_code=503, detail="Master agent not available")
        
        # Set autonomy level
        from master_agent import AutonomyLevel
        autonomy_map = {
            "manual": AutonomyLevel.MANUAL,
            "semi": AutonomyLevel.SEMI_AUTONOMOUS,
            "full": AutonomyLevel.FULLY_AUTONOMOUS,
        }
        
        if autonomy_mode not in autonomy_map:
            raise HTTPException(status_code=400, detail="Invalid autonomy mode")
        
        autopilot_app.master_agent.autonomy_level = autonomy_map[autonomy_mode]
        
        # Start autonomous operation in background
        background_tasks.add_task(run_autonomous_operation)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Autonomous operation started with {autonomy_mode} autonomy level",
            "autonomy_level": autonomy_mode
        })
    except Exception as e:
        logger.error(f"Failed to start autonomous operation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_autonomous_operation():
    """Background task for autonomous operation."""
    try:
        logger.info("Starting autonomous operation...")
        # This would run the autonomous operation logic
        # For now, just log that it's running
        while True:
            await asyncio.sleep(60)  # Check every minute
    except Exception as e:
        logger.error(f"Autonomous operation error: {e}")

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
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Get port from environment variable (Cloud Run sets PORT)
    port = int(os.environ.get("PORT", 8080))
    
    # Run the web server
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    ) 