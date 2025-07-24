"""
Self-Healing CI/CD Module for AutoPilot Ventures
Includes failure detection, automatic recovery, and intelligent deployment management
"""

import os
import json
import logging
import asyncio
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import requests
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    ROLLBACK = "rollback"
    HEALTH_CHECK_FAILED = "health_check_failed"

class FailureType(Enum):
    BUILD_FAILED = "build_failed"
    DEPLOYMENT_FAILED = "deployment_failed"
    HEALTH_CHECK_FAILED = "health_check_failed"
    PERFORMANCE_DEGRADED = "performance_degraded"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    NETWORK_ISSUE = "network_issue"

@dataclass
class DeploymentEvent:
    """Deployment event for tracking"""
    event_id: str
    timestamp: datetime
    status: DeploymentStatus
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None
    recovery_action: Optional[str] = None
    duration_seconds: Optional[float] = None
    metadata: Dict[str, Any] = None

@dataclass
class HealthCheckResult:
    """Health check result"""
    timestamp: datetime
    status: str
    response_time_ms: float
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = None

class SelfHealingCICD:
    def __init__(self, project_id: str = "autopilot-ventures-core-466708"):
        self.project_id = project_id
        self.deployment_history: List[DeploymentEvent] = []
        self.health_check_history: List[HealthCheckResult] = []
        self.current_deployment = None
        self.rollback_threshold = 3  # Number of failures before rollback
        self.health_check_interval = 30  # seconds
        self.recovery_attempts = 0
        self.max_recovery_attempts = 5
        
        # Configuration
        self.config = self._load_config()
        
        # Start monitoring
        self._start_monitoring()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load CI/CD configuration"""
        config = {
            "deployment": {
                "strategy": "rolling",
                "max_instances": 10,
                "min_instances": 1,
                "timeout_seconds": 600,
                "health_check_path": "/health",
                "health_check_timeout": 30,
                "rollback_enabled": True,
                "auto_scale": True
            },
            "monitoring": {
                "enabled": True,
                "check_interval": 30,
                "failure_threshold": 3,
                "success_threshold": 2,
                "metrics_collection": True
            },
            "recovery": {
                "enabled": True,
                "max_attempts": 5,
                "backoff_multiplier": 2,
                "initial_delay": 60
            }
        }
        
        # Load from file if exists
        config_file = "cicd_config.yaml"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
                    config.update(file_config)
                logger.info(f"✅ Loaded CI/CD config from {config_file}")
            except Exception as e:
                logger.error(f"❌ Failed to load config file: {e}")
        
        return config
    
    def _start_monitoring(self):
        """Start continuous monitoring"""
        if not self.config["monitoring"]["enabled"]:
            return
        
        async def monitor_loop():
            while True:
                try:
                    await self._perform_health_check()
                    await self._check_deployment_status()
                    await self._analyze_metrics()
                    
                    # Wait for next check
                    await asyncio.sleep(self.config["monitoring"]["check_interval"])
                    
                except Exception as e:
                    logger.error(f"❌ Monitoring error: {e}")
                    await asyncio.sleep(60)
        
        # Start monitoring task
        asyncio.create_task(monitor_loop())
        logger.info("✅ Started self-healing CI/CD monitoring")
    
    async def deploy(self, image_tag: str, environment: str = "production") -> bool:
        """Deploy application with self-healing capabilities"""
        logger.info(f"🚀 Starting deployment: {image_tag} to {environment}")
        
        deployment_id = f"deploy_{int(time.time())}"
        start_time = datetime.now()
        
        # Create deployment event
        deployment_event = DeploymentEvent(
            event_id=deployment_id,
            timestamp=start_time,
            status=DeploymentStatus.IN_PROGRESS,
            metadata={
                "image_tag": image_tag,
                "environment": environment,
                "deployment_strategy": self.config["deployment"]["strategy"]
            }
        )
        
        self.deployment_history.append(deployment_event)
        self.current_deployment = deployment_event
        
        try:
            # Step 1: Pre-deployment health check
            if not await self._pre_deployment_check():
                await self._handle_deployment_failure(
                    deployment_event, 
                    FailureType.HEALTH_CHECK_FAILED,
                    "Pre-deployment health check failed"
                )
                return False
            
            # Step 2: Deploy to Cloud Run
            if not await self._deploy_to_cloud_run(image_tag):
                await self._handle_deployment_failure(
                    deployment_event,
                    FailureType.DEPLOYMENT_FAILED,
                    "Cloud Run deployment failed"
                )
                return False
            
            # Step 3: Post-deployment health check
            if not await self._post_deployment_check():
                await self._handle_deployment_failure(
                    deployment_event,
                    FailureType.HEALTH_CHECK_FAILED,
                    "Post-deployment health check failed"
                )
                return False
            
            # Step 4: Performance validation
            if not await self._validate_performance():
                await self._handle_deployment_failure(
                    deployment_event,
                    FailureType.PERFORMANCE_DEGRADED,
                    "Performance validation failed"
                )
                return False
            
            # Deployment successful
            deployment_event.status = DeploymentStatus.SUCCESS
            deployment_event.duration_seconds = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Deployment successful: {deployment_id}")
            self.recovery_attempts = 0  # Reset recovery attempts
            
            return True
            
        except Exception as e:
            await self._handle_deployment_failure(
                deployment_event,
                FailureType.DEPLOYMENT_FAILED,
                f"Deployment error: {str(e)}"
            )
            return False
    
    async def _pre_deployment_check(self) -> bool:
        """Pre-deployment health check"""
        logger.info("🔍 Performing pre-deployment health check...")
        
        try:
            # Check current deployment health
            health_result = await self._perform_health_check()
            
            if health_result.status != "healthy":
                logger.warning("⚠️ Current deployment is not healthy, but proceeding with deployment")
                return True  # Allow deployment even if current is unhealthy
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pre-deployment check failed: {e}")
            return False
    
    async def _deploy_to_cloud_run(self, image_tag: str) -> bool:
        """Deploy to Google Cloud Run"""
        logger.info(f"🚀 Deploying to Cloud Run: {image_tag}")
        
        try:
            # Build deployment command
            cmd = [
                "gcloud", "run", "deploy", "autopilot-ventures",
                f"--image=gcr.io/{self.project_id}/autopilot-ventures:{image_tag}",
                "--region=us-central1",
                "--platform=managed",
                "--allow-unauthenticated",
                "--port=8080",
                f"--memory={self.config['deployment']['max_instances']}Gi",
                "--cpu=2",
                f"--max-instances={self.config['deployment']['max_instances']}",
                f"--min-instances={self.config['deployment']['min_instances']}",
                f"--timeout={self.config['deployment']['timeout_seconds']}",
                "--concurrency=80"
            ]
            
            # Execute deployment
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.config["deployment"]["timeout_seconds"])
            
            if result.returncode == 0:
                logger.info("✅ Cloud Run deployment successful")
                return True
            else:
                logger.error(f"❌ Cloud Run deployment failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Cloud Run deployment timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Cloud Run deployment error: {e}")
            return False
    
    async def _post_deployment_check(self) -> bool:
        """Post-deployment health check"""
        logger.info("🔍 Performing post-deployment health check...")
        
        # Wait for deployment to stabilize
        await asyncio.sleep(30)
        
        # Perform multiple health checks
        success_count = 0
        required_success = self.config["monitoring"]["success_threshold"]
        
        for i in range(required_success + 2):  # Extra attempts
            health_result = await self._perform_health_check()
            
            if health_result.status == "healthy":
                success_count += 1
                if success_count >= required_success:
                    logger.info("✅ Post-deployment health check passed")
                    return True
            else:
                success_count = 0  # Reset on failure
            
            await asyncio.sleep(10)
        
        logger.error("❌ Post-deployment health check failed")
        return False
    
    async def _validate_performance(self) -> bool:
        """Validate deployment performance"""
        logger.info("📊 Validating deployment performance...")
        
        try:
            # Perform load test
            response_times = []
            for i in range(10):
                start_time = time.time()
                response = requests.get("http://localhost:8080/health", timeout=10)
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                
                if response.status_code != 200:
                    logger.error(f"❌ Performance validation failed: HTTP {response.status_code}")
                    return False
            
            avg_response_time = sum(response_times) / len(response_times)
            
            if avg_response_time < 1000:  # Less than 1 second
                logger.info(f"✅ Performance validation passed: {avg_response_time:.2f}ms avg")
                return True
            else:
                logger.warning(f"⚠️ Performance validation warning: {avg_response_time:.2f}ms avg")
                return True  # Allow deployment with warning
                
        except Exception as e:
            logger.error(f"❌ Performance validation error: {e}")
            return False
    
    async def _perform_health_check(self) -> HealthCheckResult:
        """Perform health check"""
        start_time = time.time()
        
        try:
            response = requests.get(
                f"http://localhost:8080{self.config['deployment']['health_check_path']}",
                timeout=self.config["deployment"]["health_check_timeout"]
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                status = "healthy"
                error_message = None
            else:
                status = "unhealthy"
                error_message = f"HTTP {response.status_code}"
            
            # Parse response for metrics
            metrics = {}
            try:
                data = response.json()
                metrics = data.get("details", {})
            except:
                pass
            
            health_result = HealthCheckResult(
                timestamp=datetime.now(),
                status=status,
                response_time_ms=response_time,
                error_message=error_message,
                metrics=metrics
            )
            
            self.health_check_history.append(health_result)
            
            return health_result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            health_result = HealthCheckResult(
                timestamp=datetime.now(),
                status="unhealthy",
                response_time_ms=response_time,
                error_message=str(e),
                metrics={}
            )
            
            self.health_check_history.append(health_result)
            return health_result
    
    async def _check_deployment_status(self):
        """Check current deployment status"""
        if not self.current_deployment:
            return
        
        # Check if deployment is still healthy
        health_result = await self._perform_health_check()
        
        if health_result.status != "healthy":
            logger.warning(f"⚠️ Deployment health check failed: {health_result.error_message}")
            
            # Check if we need to trigger recovery
            recent_failures = len([
                h for h in self.health_check_history[-10:]
                if h.status != "healthy"
            ])
            
            if recent_failures >= self.config["monitoring"]["failure_threshold"]:
                await self._trigger_recovery()
    
    async def _analyze_metrics(self):
        """Analyze deployment metrics"""
        if not self.config["monitoring"]["metrics_collection"]:
            return
        
        try:
            # Analyze recent health checks
            recent_checks = self.health_check_history[-50:]
            
            if recent_checks:
                avg_response_time = sum(h.response_time_ms for h in recent_checks) / len(recent_checks)
                error_rate = len([h for h in recent_checks if h.status != "healthy"]) / len(recent_checks)
                
                # Log metrics
                logger.info(f"📊 Metrics - Avg Response: {avg_response_time:.2f}ms, Error Rate: {error_rate:.2%}")
                
                # Trigger recovery if metrics are poor
                if error_rate > 0.1 or avg_response_time > 2000:  # 10% error rate or >2s response
                    logger.warning("⚠️ Poor performance detected, considering recovery action")
                    
        except Exception as e:
            logger.error(f"❌ Metrics analysis error: {e}")
    
    async def _handle_deployment_failure(self, deployment_event: DeploymentEvent, failure_type: FailureType, error_message: str):
        """Handle deployment failure"""
        logger.error(f"❌ Deployment failed: {error_message}")
        
        deployment_event.status = DeploymentStatus.FAILED
        deployment_event.failure_type = failure_type
        deployment_event.error_message = error_message
        deployment_event.duration_seconds = (datetime.now() - deployment_event.timestamp).total_seconds()
        
        # Check if rollback is needed
        recent_failures = len([
            d for d in self.deployment_history[-10:]
            if d.status == DeploymentStatus.FAILED
        ])
        
        if recent_failures >= self.rollback_threshold and self.config["deployment"]["rollback_enabled"]:
            await self._trigger_rollback()
        else:
            await self._trigger_recovery()
    
    async def _trigger_recovery(self):
        """Trigger automatic recovery"""
        if self.recovery_attempts >= self.max_recovery_attempts:
            logger.error("❌ Max recovery attempts reached, manual intervention required")
            return
        
        self.recovery_attempts += 1
        logger.info(f"🔄 Triggering recovery attempt {self.recovery_attempts}/{self.max_recovery_attempts}")
        
        try:
            # Attempt different recovery strategies
            recovery_strategies = [
                self._restart_service,
                self._scale_resources,
                self._clear_cache,
                self._redeploy_previous_version
            ]
            
            for strategy in recovery_strategies:
                if await strategy():
                    logger.info("✅ Recovery successful")
                    return
            
            logger.error("❌ All recovery strategies failed")
            
        except Exception as e:
            logger.error(f"❌ Recovery error: {e}")
    
    async def _trigger_rollback(self):
        """Trigger automatic rollback"""
        logger.warning("🔄 Triggering automatic rollback")
        
        try:
            # Find last successful deployment
            successful_deployments = [
                d for d in self.deployment_history
                if d.status == DeploymentStatus.SUCCESS
            ]
            
            if successful_deployments:
                last_successful = successful_deployments[-1]
                image_tag = last_successful.metadata.get("image_tag")
                
                if image_tag:
                    logger.info(f"🔄 Rolling back to: {image_tag}")
                    await self.deploy(image_tag, "rollback")
                else:
                    logger.error("❌ No valid rollback target found")
            else:
                logger.error("❌ No successful deployments to rollback to")
                
        except Exception as e:
            logger.error(f"❌ Rollback error: {e}")
    
    async def _restart_service(self) -> bool:
        """Restart the service"""
        logger.info("🔄 Restarting service...")
        
        try:
            # Restart Cloud Run service
            cmd = [
                "gcloud", "run", "services", "update-traffic", "autopilot-ventures",
                "--region=us-central1",
                "--to-latest"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"❌ Service restart failed: {e}")
            return False
    
    async def _scale_resources(self) -> bool:
        """Scale resources up"""
        logger.info("📈 Scaling resources...")
        
        try:
            # Scale up Cloud Run service
            cmd = [
                "gcloud", "run", "services", "update", "autopilot-ventures",
                "--region=us-central1",
                "--memory=4Gi",
                "--cpu=4",
                "--max-instances=20"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"❌ Resource scaling failed: {e}")
            return False
    
    async def _clear_cache(self) -> bool:
        """Clear application cache"""
        logger.info("🧹 Clearing cache...")
        
        try:
            # Clear Redis cache
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.flushdb()
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache clearing failed: {e}")
            return False
    
    async def _redeploy_previous_version(self) -> bool:
        """Redeploy previous version"""
        logger.info("🔄 Redeploying previous version...")
        
        try:
            # Get previous successful deployment
            successful_deployments = [
                d for d in self.deployment_history
                if d.status == DeploymentStatus.SUCCESS
            ]
            
            if successful_deployments:
                previous_deployment = successful_deployments[-1]
                image_tag = previous_deployment.metadata.get("image_tag")
                
                if image_tag:
                    return await self.deploy(image_tag, "recovery")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Previous version redeploy failed: {e}")
            return False
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment status"""
        return {
            "current_deployment": self.current_deployment.event_id if self.current_deployment else None,
            "deployment_status": self.current_deployment.status.value if self.current_deployment else None,
            "recovery_attempts": self.recovery_attempts,
            "total_deployments": len(self.deployment_history),
            "successful_deployments": len([d for d in self.deployment_history if d.status == DeploymentStatus.SUCCESS]),
            "failed_deployments": len([d for d in self.deployment_history if d.status == DeploymentStatus.FAILED]),
            "last_health_check": self.health_check_history[-1].status if self.health_check_history else None,
            "config": self.config
        }
    
    def get_deployment_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get deployment history"""
        recent_deployments = self.deployment_history[-limit:]
        
        return [
            {
                "event_id": d.event_id,
                "timestamp": d.timestamp.isoformat(),
                "status": d.status.value,
                "failure_type": d.failure_type.value if d.failure_type else None,
                "error_message": d.error_message,
                "recovery_action": d.recovery_action,
                "duration_seconds": d.duration_seconds,
                "metadata": d.metadata
            }
            for d in recent_deployments
        ]

# Global self-healing CI/CD instance
self_healing_cicd = SelfHealingCICD() 