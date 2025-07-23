"""
FastAPI web server for AutoPilot Ventures - Google Cloud Run Deployment
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime

# Fix Unicode encoding issues on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import config
from utils import budget_manager, generate_id, log, security_utils, alert_manager, secrets_manager
from database import db_manager
from orchestrator import AgentOrchestrator
from agents import (
    NicheResearchAgent,
    MVPDesignAgent,
    MarketingStrategyAgent,
    ContentCreationAgent,
    AnalyticsAgent,
    OperationsMonetizationAgent,
    FundingInvestorAgent,
    LegalComplianceAgent,
    HRTeamBuildingAgent,
    CustomerSupportScalingAgent,
)
from master_agent import get_master_agent, AutonomyLevel

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AutoPilot Ventures",
    description="Autonomous AI-powered platform for creating, managing, and scaling businesses for personal income generation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global application instance
autopilot_app = None
master_agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global autopilot_app, master_agent
    
    try:
        logger.info("🚀 Starting AutoPilot Ventures Platform...")
        
        # Initialize the main application
        autopilot_app = AutoPilotVenturesApp()
        
        # Initialize master agent
        try:
            autonomy_level = AutonomyLevel.SEMI_AUTONOMOUS
            master_agent = get_master_agent(autonomy_level)
            logger.info(f"Master Agent initialized with autonomy level: {autonomy_level.value}")
        except Exception as e:
            logger.warning(f"Master Agent initialization failed: {e}")
            master_agent = None
        
        logger.info("✅ AutoPilot Ventures Platform started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start AutoPilot Ventures Platform: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global autopilot_app, master_agent
    
    try:
        logger.info("🔄 Shutting down AutoPilot Ventures Platform...")
        
        if master_agent:
            master_agent.shutdown()
        
        if autopilot_app:
            await graceful_shutdown(autopilot_app)
        
        logger.info("✅ Shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

class AutoPilotVenturesApp:
    """Enhanced main application class for personal income generation."""

    def __init__(self):
        """Initialize the application."""
        self.startup_id = None
        self.orchestrator = None
        self.agents = {}
        self.master_agent = None
        self._initialize_agents()
        self._initialize_master_agent()

    def _initialize_agents(self) -> None:
        """Initialize all 10 AI agents for autonomous business creation."""
        try:
            # Create a temporary startup ID for agent initialization
            temp_startup_id = generate_id("startup")

            self.agents = {
                "niche_research": NicheResearchAgent(temp_startup_id),
                "mvp_design": MVPDesignAgent(temp_startup_id),
                "marketing_strategy": MarketingStrategyAgent(temp_startup_id),
                "content_creation": ContentCreationAgent(temp_startup_id),
                "analytics": AnalyticsAgent(temp_startup_id),
                "operations_monetization": OperationsMonetizationAgent(temp_startup_id),
                "funding_investor": FundingInvestorAgent(temp_startup_id),
                "legal_compliance": LegalComplianceAgent(temp_startup_id),
                "hr_team_building": HRTeamBuildingAgent(temp_startup_id),
                "customer_support_scaling": CustomerSupportScalingAgent(temp_startup_id),
            }
            logger.info(f"Initialized {len(self.agents)} AI agents")
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise

    def _initialize_master_agent(self) -> None:
        """Initialize the master agent for autonomous business operation."""
        try:
            # Initialize with semi-autonomous level by default
            autonomy_level = AutonomyLevel.SEMI_AUTONOMOUS
            self.master_agent = get_master_agent(autonomy_level)
            logger.info(f"Master Agent initialized with autonomy level: {autonomy_level.value}")
        except Exception as e:
            logger.error(f"Failed to initialize master agent: {e}")
            # Don't raise - master agent is optional for basic operation

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "checks": {},
        }

        try:
            # Database health check
            try:
                stats = db_manager.get_database_stats()
                health_status["checks"]["database"] = {
                    "status": "healthy",
                    "startups_count": stats["startups"],
                    "agents_count": stats["agents"],
                    "executions_count": stats["executions"],
                }
            except Exception as e:
                health_status["checks"]["database"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health_status["status"] = "unhealthy"

            # Budget health check
            try:
                budget_status = budget_manager.get_budget_status()
                health_status["checks"]["budget"] = {
                    "status": "healthy",
                    "remaining": budget_status["remaining"],
                    "spent": budget_status["spent"],
                    "initial": budget_status["initial"],
                }
            except Exception as e:
                health_status["checks"]["budget"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health_status["status"] = "unhealthy"

            # Security health check
            try:
                security_status = security_utils.check_security_status()
                health_status["checks"]["security"] = {
                    "status": "healthy",
                    "encryption_enabled": security_status["encryption_enabled"],
                    "content_safety_enabled": security_status["content_safety_enabled"],
                }
            except Exception as e:
                health_status["checks"]["security"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health_status["status"] = "unhealthy"

            # Agents health check
            try:
                agent_status = {}
                for agent_type, agent in self.agents.items():
                    agent_status[agent_type] = {
                        "status": "healthy",
                        "execution_count": agent.execution_count,
                        "success_rate": agent.success_rate,
                        "average_cost": agent.average_cost,
                    }
                health_status["checks"]["agents"] = {
                    "status": "healthy",
                    "agents": agent_status,
                }
            except Exception as e:
                health_status["checks"]["agents"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health_status["status"] = "unhealthy"

            # Configuration health check
            try:
                config_status = {
                    "environment": config.environment,
                    "log_level": config.log_level,
                    "autonomy_level": config.autonomy_level,
                    "budget_threshold": config.budget_threshold,
                }
                health_status["checks"]["configuration"] = {
                    "status": "healthy",
                    "config": config_status,
                }
            except Exception as e:
                health_status["checks"]["configuration"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health_status["status"] = "unhealthy"

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)

        return health_status

    async def create_business(self, name: str, description: str, niche: str, language: str = "en") -> Dict[str, Any]:
        """Create a new business with the specified parameters."""
        try:
            # Generate startup ID
            startup_id = generate_id("startup")
            self.startup_id = startup_id

            # Initialize orchestrator
            self.orchestrator = AgentOrchestrator(startup_id)

            # Create startup record
            startup_data = {
                "id": startup_id,
                "name": name,
                "description": description,
                "niche": niche,
                "language": language,
                "status": "created",
                "created_at": datetime.utcnow().isoformat(),
            }

            # Save to database
            db_manager.create_startup(startup_data)

            # Run initial workflow
            workflow_config = {
                "niche_research": {
                    "niche": niche,
                    "language": language,
                    "market_analysis": True,
                },
                "mvp_design": {
                    "startup_name": name,
                    "description": description,
                    "niche": niche,
                },
                "marketing_strategy": {
                    "startup_name": name,
                    "niche": niche,
                    "language": language,
                },
            }

            workflow_result = await self.orchestrator.execute_workflow(workflow_config)

            return {
                "success": True,
                "startup_id": startup_id,
                "startup_data": startup_data,
                "workflow_result": workflow_result,
                "message": f"Business '{name}' created successfully in {niche} niche",
            }

        except Exception as e:
            logger.error(f"Failed to create business: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create business",
            }

    async def run_workflow(self, workflow_config: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """Run a complete workflow with the specified configuration."""
        try:
            if not self.orchestrator:
                startup_id = generate_id("startup")
                self.orchestrator = AgentOrchestrator(startup_id)

            result = await self.orchestrator.execute_workflow(workflow_config)
            return {
                "success": True,
                "workflow_result": result,
                "message": "Workflow executed successfully",
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Workflow execution failed",
            }

    async def run_single_agent(self, agent_type: str, **kwargs) -> Dict[str, Any]:
        """Run a single agent with the specified parameters."""
        try:
            if not self.orchestrator:
                startup_id = generate_id("startup")
                self.orchestrator = AgentOrchestrator(startup_id)

            result = await self.orchestrator.execute_single_agent(agent_type, **kwargs)
            return {
                "success": True,
                "agent_result": result,
                "message": f"Agent {agent_type} executed successfully",
            }

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Agent {agent_type} execution failed",
            }

    def get_platform_status(self) -> Dict[str, Any]:
        """Get comprehensive platform status."""
        try:
            # Get database stats
            db_stats = db_manager.get_database_stats()

            # Get budget status
            budget_status = budget_manager.get_budget_status()

            # Get agent performance
            agent_performance = {}
            for agent_type, agent in self.agents.items():
                agent_performance[agent_type] = {
                    "execution_count": agent.execution_count,
                    "success_rate": agent.success_rate,
                    "average_cost": agent.average_cost,
                    "last_execution": agent.last_execution.isoformat() if agent.last_execution else None,
                }

            return {
                "platform_version": "2.0.0",
                "status": "operational",
                "timestamp": datetime.utcnow().isoformat(),
                "database_stats": db_stats,
                "budget_status": budget_status,
                "agent_performance": agent_performance,
                "total_agents": len(self.agents),
                "supported_languages": ["en", "es", "zh", "fr", "de", "ar", "pt", "hi", "ru", "ja"],
                "autonomy_level": config.autonomy_level,
                "environment": config.environment,
            }

        except Exception as e:
            logger.error(f"Failed to get platform status: {e}")
            return {
                "platform_version": "2.0.0",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def multilingual_demo(self, language: str = "en") -> Dict[str, Any]:
        """Run a multilingual demonstration."""
        try:
            # Create a demo startup
            demo_name = f"Demo Startup ({language.upper()})"
            demo_description = f"Multilingual demonstration startup in {language}"
            demo_niche = "Technology"

            result = await self.create_business(demo_name, demo_description, demo_niche, language)

            if result["success"]:
                # Run a simple workflow
                workflow_config = {
                    "content_creation": {
                        "startup_name": demo_name,
                        "content_type": "landing_page",
                        "language": language,
                        "tone": "professional",
                    }
                }

                workflow_result = await self.run_workflow(workflow_config, language)

                return {
                    "success": True,
                    "demo_startup": result["startup_data"],
                    "workflow_result": workflow_result,
                    "language": language,
                    "message": f"Multilingual demo completed successfully in {language}",
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Multilingual demo failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Multilingual demo failed for language {language}",
            }

async def graceful_shutdown(app: AutoPilotVenturesApp, timeout: int = 30) -> None:
    """Gracefully shutdown the application."""
    try:
        logger.info("🔄 Starting graceful shutdown...")

        # Stop master agent if running
        if app.master_agent:
            try:
                app.master_agent.shutdown()
                logger.info("✅ Master agent shutdown complete")
            except Exception as e:
                logger.warning(f"⚠️  Master agent shutdown error: {e}")

        # Cancel any pending tasks
        try:
            tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
            if tasks:
                logger.info(f"🔄 Cancelling {len(tasks)} pending tasks...")
                for task in tasks:
                    task.cancel()
                
                # Wait for tasks to complete with timeout
                await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=timeout)
                logger.info("✅ Task cancellation complete")
        except asyncio.TimeoutError:
            logger.warning(f"⚠️  Task cancellation timed out after {timeout} seconds")
        except Exception as e:
            logger.warning(f"⚠️  Task cancellation error: {e}")

        # Close database connections
        try:
            db_manager.close_connections()
            logger.info("✅ Database connections closed")
        except Exception as e:
            logger.warning(f"⚠️  Database connection closure error: {e}")

        logger.info("✅ Graceful shutdown complete")

    except Exception as e:
        logger.error(f"❌ Graceful shutdown failed: {e}")

# API Routes

@app.get("/")
async def root():
    """Root endpoint with platform information."""
    return {
        "message": "AutoPilot Ventures Platform",
        "version": "2.0.0",
        "description": "Autonomous AI-powered platform for creating, managing, and scaling businesses for personal income generation",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "create_business": "/create_business",
            "run_workflow": "/run_workflow",
            "run_agent": "/run_agent",
            "multilingual_demo": "/multilingual_demo",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    health_status = await autopilot_app.health_check()
    
    if health_status["status"] == "healthy":
        return JSONResponse(content=health_status, status_code=200)
    else:
        return JSONResponse(content=health_status, status_code=503)

@app.get("/status")
async def get_status():
    """Get platform status."""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    return autopilot_app.get_platform_status()

@app.post("/create_business")
async def create_business_endpoint(
    name: str,
    description: str,
    niche: str,
    language: str = "en"
):
    """Create a new business."""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    result = await autopilot_app.create_business(name, description, niche, language)
    
    if result["success"]:
        return JSONResponse(content=result, status_code=201)
    else:
        return JSONResponse(content=result, status_code=400)

@app.post("/run_workflow")
async def run_workflow_endpoint(workflow_config: Dict[str, Any], language: str = "en"):
    """Run a workflow."""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    result = await autopilot_app.run_workflow(workflow_config, language)
    
    if result["success"]:
        return result
    else:
        return JSONResponse(content=result, status_code=400)

@app.post("/run_agent")
async def run_agent_endpoint(agent_type: str, config: Dict[str, Any]):
    """Run a single agent."""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    result = await autopilot_app.run_single_agent(agent_type, **config)
    
    if result["success"]:
        return result
    else:
        return JSONResponse(content=result, status_code=400)

@app.post("/multilingual_demo")
async def multilingual_demo_endpoint(language: str = "en"):
    """Run multilingual demonstration."""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    result = await autopilot_app.multilingual_demo(language)
    
    if result["success"]:
        return result
    else:
        return JSONResponse(content=result, status_code=400)

@app.get("/master_status")
async def get_master_status():
    """Get master agent status."""
    if not master_agent:
        raise HTTPException(status_code=503, detail="Master agent not available")
    
    return master_agent.get_master_status()

@app.get("/income_report")
async def get_income_report():
    """Get income projection report."""
    if not master_agent:
        raise HTTPException(status_code=503, detail="Master agent not available")
    
    return master_agent.get_income_summary()

if __name__ == "__main__":
    # Get port from environment variable (Google Cloud Run uses PORT=8080)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting AutoPilot Ventures web server on {host}:{port}")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True
    ) 