"""
Health Monitoring System for AutoPilot Ventures
Includes health checks, startup probes, and comprehensive monitoring
"""

import os
import time
import asyncio
import logging
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    DEGRADED = "degraded"

@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration_ms: float
    details: Dict[str, Any] = None

class HealthMonitor:
    def __init__(self):
        self.startup_time = datetime.now()
        self.health_checks: List[HealthCheck] = []
        self.startup_probes: List[HealthCheck] = []
        self.system_metrics = {}
        
    async def startup_probe(self) -> bool:
        """Startup probe to check if the application is ready to serve traffic"""
        logger.info("🔍 Running startup probe...")
        
        checks = [
            ("database_connection", self._check_database),
            ("redis_connection", self._check_redis),
            ("ai_services", self._check_ai_services),
            ("file_system", self._check_file_system),
            ("memory_usage", self._check_memory),
            ("disk_space", self._check_disk_space),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                start_time = time.time()
                result = await check_func()
                duration = (time.time() - start_time) * 1000
                
                probe = HealthCheck(
                    name=check_name,
                    status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                    message=f"Startup probe {check_name}: {'PASSED' if result else 'FAILED'}",
                    timestamp=datetime.now(),
                    duration_ms=duration
                )
                self.startup_probes.append(probe)
                
                if not result:
                    all_passed = False
                    logger.error(f"❌ Startup probe failed: {check_name}")
                else:
                    logger.info(f"✅ Startup probe passed: {check_name}")
                    
            except Exception as e:
                logger.error(f"❌ Startup probe error in {check_name}: {e}")
                all_passed = False
                
        return all_passed
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for the application"""
        logger.info("🏥 Running health check...")
        
        checks = [
            ("api_endpoints", self._check_api_endpoints),
            ("database_health", self._check_database_health),
            ("redis_health", self._check_redis_health),
            ("ai_services_health", self._check_ai_services_health),
            ("system_resources", self._check_system_resources),
            ("business_metrics", self._check_business_metrics),
        ]
        
        results = {}
        overall_status = HealthStatus.HEALTHY
        
        for check_name, check_func in checks:
            try:
                start_time = time.time()
                result = await check_func()
                duration = (time.time() - start_time) * 1000
                
                health_check = HealthCheck(
                    name=check_name,
                    status=result.get('status', HealthStatus.UNHEALTHY),
                    message=result.get('message', 'Health check completed'),
                    timestamp=datetime.now(),
                    duration_ms=duration,
                    details=result.get('details', {})
                )
                self.health_checks.append(health_check)
                
                results[check_name] = {
                    'status': health_check.status.value,
                    'message': health_check.message,
                    'duration_ms': health_check.duration_ms,
                    'details': health_check.details
                }
                
                if health_check.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif health_check.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                    
            except Exception as e:
                logger.error(f"❌ Health check error in {check_name}: {e}")
                results[check_name] = {
                    'status': HealthStatus.UNHEALTHY.value,
                    'message': f'Error: {str(e)}',
                    'duration_ms': 0,
                    'details': {}
                }
                overall_status = HealthStatus.UNHEALTHY
        
        return {
            'status': overall_status.value,
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.startup_time).total_seconds(),
            'checks': results,
            'system_metrics': self._get_system_metrics()
        }
    
    async def _check_database(self) -> bool:
        """Check database connectivity"""
        try:
            # Import here to avoid startup issues
            from database import DatabaseManager
            db = DatabaseManager()
            await db.test_connection()
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    async def _check_redis(self) -> bool:
        """Check Redis connectivity"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=5)
            r.ping()
            return True
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            return False
    
    async def _check_ai_services(self) -> bool:
        """Check AI services availability"""
        try:
            # Check OpenAI API
            import openai
            response = openai.Model.list()
            return True
        except Exception as e:
            logger.error(f"AI services check failed: {e}")
            return False
    
    async def _check_file_system(self) -> bool:
        """Check file system permissions and space"""
        try:
            # Check if we can write to logs directory
            log_dir = "/app/logs"
            test_file = os.path.join(log_dir, "health_test.txt")
            
            with open(test_file, 'w') as f:
                f.write("health test")
            
            os.remove(test_file)
            return True
        except Exception as e:
            logger.error(f"File system check failed: {e}")
            return False
    
    async def _check_memory(self) -> bool:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            return memory.percent < 90  # Less than 90% usage
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return False
    
    async def _check_disk_space(self) -> bool:
        """Check disk space"""
        try:
            disk = psutil.disk_usage('/')
            return disk.percent < 90  # Less than 90% usage
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return False
    
    async def _check_api_endpoints(self) -> Dict[str, Any]:
        """Check API endpoints health"""
        try:
            endpoints = [
                "/health",
                "/status",
                "/metrics"
            ]
            
            results = {}
            for endpoint in endpoints:
                try:
                    response = requests.get(f"http://localhost:8080{endpoint}", timeout=5)
                    results[endpoint] = {
                        'status_code': response.status_code,
                        'response_time_ms': response.elapsed.total_seconds() * 1000
                    }
                except Exception as e:
                    results[endpoint] = {'error': str(e)}
            
            healthy_endpoints = sum(1 for r in results.values() if 'status_code' in r and r['status_code'] == 200)
            total_endpoints = len(endpoints)
            
            if healthy_endpoints == total_endpoints:
                status = HealthStatus.HEALTHY
                message = f"All {total_endpoints} endpoints healthy"
            elif healthy_endpoints > total_endpoints * 0.5:
                status = HealthStatus.DEGRADED
                message = f"{healthy_endpoints}/{total_endpoints} endpoints healthy"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Only {healthy_endpoints}/{total_endpoints} endpoints healthy"
            
            return {
                'status': status,
                'message': message,
                'details': results
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'API health check failed: {e}',
                'details': {}
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            from database import DatabaseManager
            db = DatabaseManager()
            
            # Check connection pool
            pool_status = await db.get_pool_status()
            
            # Check query performance
            start_time = time.time()
            await db.execute_query("SELECT 1")
            query_time = (time.time() - start_time) * 1000
            
            if query_time < 100 and pool_status['active_connections'] < pool_status['max_connections'] * 0.8:
                status = HealthStatus.HEALTHY
                message = "Database healthy"
            elif query_time < 500:
                status = HealthStatus.DEGRADED
                message = "Database performance degraded"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Database unhealthy"
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'query_time_ms': query_time,
                    'pool_status': pool_status
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'Database health check failed: {e}',
                'details': {}
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=5)
            
            start_time = time.time()
            r.ping()
            ping_time = (time.time() - start_time) * 1000
            
            info = r.info()
            
            if ping_time < 10 and info['used_memory_human'] != '0B':
                status = HealthStatus.HEALTHY
                message = "Redis healthy"
            elif ping_time < 50:
                status = HealthStatus.DEGRADED
                message = "Redis performance degraded"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Redis unhealthy"
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'ping_time_ms': ping_time,
                    'memory_usage': info['used_memory_human'],
                    'connected_clients': info['connected_clients']
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'Redis health check failed: {e}',
                'details': {}
            }
    
    async def _check_ai_services_health(self) -> Dict[str, Any]:
        """Check AI services health"""
        try:
            import openai
            
            start_time = time.time()
            models = openai.Model.list()
            api_time = (time.time() - start_time) * 1000
            
            if api_time < 1000 and len(models.data) > 0:
                status = HealthStatus.HEALTHY
                message = "AI services healthy"
            elif api_time < 5000:
                status = HealthStatus.DEGRADED
                message = "AI services performance degraded"
            else:
                status = HealthStatus.UNHEALTHY
                message = "AI services unhealthy"
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'api_response_time_ms': api_time,
                    'available_models': len(models.data)
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'AI services health check failed: {e}',
                'details': {}
            }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            if cpu_percent < 80 and memory.percent < 80 and disk.percent < 80:
                status = HealthStatus.HEALTHY
                message = "System resources healthy"
            elif cpu_percent < 95 and memory.percent < 95 and disk.percent < 95:
                status = HealthStatus.DEGRADED
                message = "System resources under pressure"
            else:
                status = HealthStatus.UNHEALTHY
                message = "System resources critical"
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'System resources check failed: {e}',
                'details': {}
            }
    
    async def _check_business_metrics(self) -> Dict[str, Any]:
        """Check business metrics health"""
        try:
            # This would check business-specific metrics
            # For now, return healthy status
            return {
                'status': HealthStatus.HEALTHY,
                'message': "Business metrics healthy",
                'details': {
                    'active_businesses': 0,
                    'total_revenue': 0,
                    'conversion_rate': 0
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY,
                'message': f'Business metrics check failed: {e}',
                'details': {}
            }
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'uptime_seconds': (datetime.now() - self.startup_time).total_seconds()
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {}

# Global health monitor instance
health_monitor = HealthMonitor() 