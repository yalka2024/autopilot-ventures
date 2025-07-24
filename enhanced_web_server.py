"""
Enhanced Web Server with Health Checks, BigQuery Analytics, and Self-Healing CI/CD
"""

import os
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import our monitoring systems
from health_monitoring import health_monitor, HealthStatus
from bigquery_analytics import bigquery_analytics, RequestLog, BusinessMetric, SystemMetric
from self_healing_cicd import self_healing_cicd, DeploymentStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global app instance
autopilot_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global autopilot_app
    
    # Startup
    logger.info("🚀 Starting AutoPilot Ventures Enhanced Server...")
    
    try:
        # Initialize main application
        from main import AutoPilotVenturesApp
        autopilot_app = AutoPilotVenturesApp()
        await autopilot_app.initialize()
        
        # Run startup probe
        startup_success = await health_monitor.startup_probe()
        if not startup_success:
            logger.error("❌ Startup probe failed")
            autopilot_app = None
        else:
            logger.info("✅ Startup probe passed")
        
        # Log system startup metric
        system_metric = SystemMetric(
            timestamp=datetime.now().isoformat(),
            metric_name="system_startup",
            metric_value=1.0,
            metric_unit="boolean",
            component="web_server",
            tags={"status": "success" if startup_success else "failed"}
        )
        bigquery_analytics.log_system_metric(system_metric)
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
        autopilot_app = None
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AutoPilot Ventures Enhanced Server...")
    
    # Flush BigQuery data
    await bigquery_analytics.flush_all()
    
    # Log system shutdown metric
    shutdown_metric = SystemMetric(
        timestamp=datetime.now().isoformat(),
        metric_name="system_shutdown",
        metric_value=1.0,
        metric_unit="boolean",
        component="web_server",
        tags={"status": "normal"}
    )
    bigquery_analytics.log_system_metric(shutdown_metric)

# Create FastAPI app
app = FastAPI(
    title="AutoPilot Ventures Enhanced",
    description="Self-healing autonomous business platform with health monitoring and analytics",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Middleware to log all requests for analytics"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Process request
    try:
        response = await call_next(request)
        response_time = (time.time() - start_time) * 1000
        
        # Log request for analytics
        request_log = RequestLog(
            timestamp=datetime.now().isoformat(),
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            response_time_ms=response_time,
            user_agent=request.headers.get("user-agent", ""),
            ip_address=request.client.host if request.client else "",
            user_id=request.headers.get("x-user-id"),
            session_id=request.headers.get("x-session-id"),
            business_id=request.headers.get("x-business-id"),
            language=request.headers.get("accept-language", "en").split(",")[0],
            error_message=None
        )
        
        bigquery_analytics.log_request(request_log)
        
        # Add response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = str(response_time)
        
        return response
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        
        # Log error request
        request_log = RequestLog(
            timestamp=datetime.now().isoformat(),
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=500,
            response_time_ms=response_time,
            user_agent=request.headers.get("user-agent", ""),
            ip_address=request.client.host if request.client else "",
            user_id=request.headers.get("x-user-id"),
            session_id=request.headers.get("x-session-id"),
            business_id=request.headers.get("x-business-id"),
            language=request.headers.get("accept-language", "en").split(",")[0],
            error_message=str(e)
        )
        
        bigquery_analytics.log_request(request_log)
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "request_id": request_id}
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AutoPilot Ventures Enhanced Platform",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Health Monitoring",
            "BigQuery Analytics",
            "Self-Healing CI/CD",
            "Autonomous Business Management"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Enhanced health check endpoint"""
    try:
        # Perform comprehensive health check
        health_result = await health_monitor.health_check()
        
        # Log health check metric
        health_metric = SystemMetric(
            timestamp=datetime.now().isoformat(),
            metric_name="health_check",
            metric_value=1.0 if health_result["status"] == "healthy" else 0.0,
            metric_unit="boolean",
            component="web_server",
            tags={
                "status": health_result["status"],
                "uptime_seconds": str(health_result["uptime_seconds"])
            }
        )
        bigquery_analytics.log_system_metric(health_metric)
        
        return health_result
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/status")
async def status():
    """System status endpoint"""
    try:
        # Get deployment status
        deployment_status = self_healing_cicd.get_deployment_status()
        
        # Get recent health checks
        recent_health = health_monitor.health_checks[-5:] if health_monitor.health_checks else []
        
        return {
            "system": {
                "status": "operational" if autopilot_app else "initializing",
                "uptime_seconds": deployment_status.get("uptime_seconds", 0),
                "version": "2.0.0"
            },
            "deployment": deployment_status,
            "health": {
                "recent_checks": [
                    {
                        "timestamp": h.timestamp.isoformat(),
                        "status": h.status.value,
                        "duration_ms": h.duration_ms
                    }
                    for h in recent_health
                ]
            },
            "analytics": {
                "bigquery_enabled": bigquery_analytics.client is not None,
                "pending_logs": len(bigquery_analytics.request_logs_queue),
                "pending_metrics": len(bigquery_analytics.business_metrics_queue) + len(bigquery_analytics.system_metrics_queue)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Status check error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/metrics")
async def metrics():
    """System metrics endpoint"""
    try:
        # Get system metrics
        system_metrics = health_monitor._get_system_metrics()
        
        # Get deployment metrics
        deployment_metrics = {
            "total_deployments": len(self_healing_cicd.deployment_history),
            "successful_deployments": len([d for d in self_healing_cicd.deployment_history if d.status == DeploymentStatus.SUCCESS]),
            "failed_deployments": len([d for d in self_healing_cicd.deployment_history if d.status == DeploymentStatus.FAILED]),
            "recovery_attempts": self_healing_cicd.recovery_attempts
        }
        
        # Get analytics metrics
        analytics_metrics = {
            "pending_request_logs": len(bigquery_analytics.request_logs_queue),
            "pending_business_metrics": len(bigquery_analytics.business_metrics_queue),
            "pending_system_metrics": len(bigquery_analytics.system_metrics_queue)
        }
        
        return {
            "system": system_metrics,
            "deployment": deployment_metrics,
            "analytics": analytics_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Metrics error: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/deployment/history")
async def deployment_history(limit: int = 10):
    """Get deployment history"""
    try:
        history = self_healing_cicd.get_deployment_history(limit)
        return {
            "deployments": history,
            "total": len(self_healing_cicd.deployment_history),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Deployment history error: {e}")
        return {"error": str(e)}

@app.post("/deployment/trigger")
async def trigger_deployment(image_tag: str, environment: str = "production"):
    """Trigger a new deployment"""
    try:
        success = await self_healing_cicd.deploy(image_tag, environment)
        
        return {
            "success": success,
            "image_tag": image_tag,
            "environment": environment,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Deployment trigger error: {e}")
        return {"error": str(e)}

@app.post("/analytics/flush")
async def flush_analytics():
    """Flush pending analytics data to BigQuery"""
    try:
        await bigquery_analytics.flush_all()
        return {
            "success": True,
            "message": "Analytics data flushed to BigQuery",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Analytics flush error: {e}")
        return {"error": str(e)}

@app.get("/analytics/queries")
async def get_analytics_queries():
    """Get sample analytics queries"""
    try:
        queries = {
            "request_analysis": bigquery_analytics.get_analytics_query("request_analysis"),
            "business_performance": bigquery_analytics.get_analytics_query("business_performance"),
            "system_health": bigquery_analytics.get_analytics_query("system_health")
        }
        
        return {
            "queries": queries,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Analytics queries error: {e}")
        return {"error": str(e)}

# Business endpoints (if autopilot_app is available)
@app.get("/business/status")
async def business_status():
    """Get business status"""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    try:
        # Log business metric
        business_metric = BusinessMetric(
            timestamp=datetime.now().isoformat(),
            business_id="system",
            metric_name="api_calls",
            metric_value=1.0,
            metric_unit="count",
            category="api_usage",
            tags={"endpoint": "/business/status"}
        )
        bigquery_analytics.log_business_metric(business_metric)
        
        return await autopilot_app.get_business_status()
    except Exception as e:
        logger.error(f"❌ Business status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/business/create")
async def create_business(business_data: Dict[str, Any]):
    """Create a new business"""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    try:
        result = await autopilot_app.create_business(business_data)
        
        # Log business creation metric
        business_metric = BusinessMetric(
            timestamp=datetime.now().isoformat(),
            business_id=result.get("business_id", "unknown"),
            metric_name="business_created",
            metric_value=1.0,
            metric_unit="count",
            category="business_operations",
            tags={"language": business_data.get("language", "en")}
        )
        bigquery_analytics.log_business_metric(business_metric)
        
        return result
    except Exception as e:
        logger.error(f"❌ Business creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demo/{language}")
async def demo(language: str):
    """Run demo in specified language"""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    try:
        result = await autopilot_app.run_demo(language)
        
        # Log demo metric
        business_metric = BusinessMetric(
            timestamp=datetime.now().isoformat(),
            business_id="demo",
            metric_name="demo_executed",
            metric_value=1.0,
            metric_unit="count",
            category="demo_operations",
            tags={"language": language}
        )
        bigquery_analytics.log_business_metric(business_metric)
        
        return result
    except Exception as e:
        logger.error(f"❌ Demo error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(request_data: Dict[str, Any]):
    """Chat endpoint for multilingual testing"""
    try:
        prompt = request_data.get("prompt", "")
        language = request_data.get("language", "en")
        
        if not autopilot_app:
            # Fallback response if app not initialized
            return {
                "response": f"AutoPilot Ventures is starting up. Your prompt: {prompt}",
                "language": language,
                "timestamp": datetime.now().isoformat()
            }
        
        # Use the autopilot app to process the chat
        result = await autopilot_app.process_chat(prompt, language)
        
        # Log chat metric
        business_metric = BusinessMetric(
            timestamp=datetime.now().isoformat(),
            business_id="chat",
            metric_name="chat_requests",
            metric_value=1.0,
            metric_unit="count",
            category="user_interaction",
            tags={"language": language, "prompt_length": str(len(prompt))}
        )
        bigquery_analytics.log_business_metric(business_metric)
        
        return {
            "response": result,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {e}")
        return {
            "response": f"Error processing request: {str(e)}",
            "language": language if 'language' in locals() else "en",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational" if autopilot_app else "initializing",
        "version": "2.0.0",
        "features": [
            "Health Monitoring",
            "BigQuery Analytics", 
            "Self-Healing CI/CD",
            "Multilingual Support"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/business/create")
async def api_create_business(business_data: Dict[str, Any]):
    """API endpoint for business creation"""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    try:
        result = await autopilot_app.create_business(business_data)
        
        # Log business creation metric
        business_metric = BusinessMetric(
            timestamp=datetime.now().isoformat(),
            business_id=result.get("business_id", "unknown"),
            metric_name="business_created",
            metric_value=1.0,
            metric_unit="count",
            category="business_operations",
            tags={"language": business_data.get("language", "en")}
        )
        bigquery_analytics.log_business_metric(business_metric)
        
        return result
    except Exception as e:
        logger.error(f"❌ API business creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/business/{business_id}")
async def api_get_business(business_id: str):
    """API endpoint to get business details"""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    try:
        result = await autopilot_app.get_business(business_id)
        
        # Log business access metric
        business_metric = BusinessMetric(
            timestamp=datetime.now().isoformat(),
            business_id=business_id,
            metric_name="business_accessed",
            metric_value=1.0,
            metric_unit="count",
            category="business_operations"
        )
        bigquery_analytics.log_business_metric(business_metric)
        
        return result
    except Exception as e:
        logger.error(f"❌ API get business error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflow/run")
async def api_run_workflow(workflow_data: Dict[str, Any]):
    """API endpoint to run business workflow"""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    try:
        result = await autopilot_app.run_workflow(workflow_data)
        
        # Log workflow execution metric
        business_metric = BusinessMetric(
            timestamp=datetime.now().isoformat(),
            business_id=workflow_data.get("business_id", "unknown"),
            metric_name="workflow_executed",
            metric_value=1.0,
            metric_unit="count",
            category="workflow_operations",
            tags={"workflow_type": workflow_data.get("type", "unknown")}
        )
        bigquery_analytics.log_business_metric(business_metric)
        
        return result
    except Exception as e:
        logger.error(f"❌ API workflow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/languages")
async def api_get_languages():
    """API endpoint to get supported languages"""
    languages = [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "it", "name": "Italian"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "ru", "name": "Russian"},
        {"code": "zh", "name": "Chinese"},
        {"code": "ja", "name": "Japanese"},
        {"code": "ko", "name": "Korean"},
        {"code": "ar", "name": "Arabic"},
        {"code": "hi", "name": "Hindi"},
        {"code": "tr", "name": "Turkish"},
        {"code": "nl", "name": "Dutch"},
        {"code": "sv", "name": "Swedish"}
    ]
    
    return {
        "languages": languages,
        "count": len(languages),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Starting enhanced server on port {port}")
    
    uvicorn.run(
        "enhanced_web_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    ) 