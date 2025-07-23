"""
Enhanced Monitoring System for AutoPilot Ventures
Comprehensive monitoring for performance, security, and quality assurance
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import aiohttp
import redis
from prometheus_client import Counter, Histogram, Gauge, Summary, Info
import structlog
import psutil
import os

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@dataclass
class Alert:
    id: str
    type: str
    severity: str
    message: str
    timestamp: datetime
    business_id: Optional[str] = None
    agent_id: Optional[str] = None
    resolved: bool = False
    resolution_time: Optional[datetime] = None

class PerformanceMonitor:
    """Enhanced performance monitoring with real-time metrics"""
    
    def __init__(self):
        # Performance metrics
        self.response_time = Histogram('api_response_time_seconds', 'API response time', ['endpoint', 'method'])
        self.request_count = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method', 'status'])
        self.error_count = Counter('api_errors_total', 'Total API errors', ['endpoint', 'error_type'])
        self.active_connections = Gauge('active_connections', 'Active database connections')
        self.queue_size = Gauge('queue_size', 'Queue size', ['queue_name'])
        self.memory_usage = Gauge('memory_usage_bytes', 'Memory usage in bytes')
        self.cpu_usage = Gauge('cpu_usage_percentage', 'CPU usage percentage')
        self.disk_usage = Gauge('disk_usage_percentage', 'Disk usage percentage')
        
        # Business metrics
        self.businesses_created = Counter('businesses_created_total', 'Total businesses created')
        self.businesses_active = Gauge('businesses_active', 'Currently active businesses')
        self.businesses_failed = Counter('businesses_failed_total', 'Total failed businesses')
        self.revenue_generated = Gauge('revenue_generated_dollars', 'Total revenue generated')
        self.profit_margin = Gauge('profit_margin_percentage', 'Average profit margin')
        
        # Agent metrics
        self.agent_executions = Counter('agent_executions_total', 'Agent executions', ['agent_type', 'status'])
        self.agent_execution_time = Histogram('agent_execution_time_seconds', 'Agent execution time', ['agent_type'])
        self.agent_errors = Counter('agent_errors_total', 'Agent errors', ['agent_type', 'error_type'])
        
        self.alert_thresholds = {
            'response_time_ms': 2000,
            'cpu_usage_percent': 80,
            'memory_usage_percent': 85,
            'disk_usage_percent': 90,
            'error_rate_percent': 5
        }
    
    async def monitor_system_performance(self) -> Dict[str, Any]:
        """Monitor system performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Update metrics
            self.cpu_usage.set(cpu_percent)
            self.memory_usage.set(memory.used)
            self.disk_usage.set((disk.used / disk.total) * 100)
            
            # Check thresholds
            alerts = []
            
            if cpu_percent > self.alert_thresholds['cpu_usage_percent']:
                alerts.append({
                    'type': 'performance',
                    'severity': 'warning',
                    'message': f'High CPU usage: {cpu_percent}%'
                })
            
            if memory.percent > self.alert_thresholds['memory_usage_percent']:
                alerts.append({
                    'type': 'performance',
                    'severity': 'warning',
                    'message': f'High memory usage: {memory.percent}%'
                })
            
            if (disk.used / disk.total) * 100 > self.alert_thresholds['disk_usage_percent']:
                alerts.append({
                    'type': 'performance',
                    'severity': 'critical',
                    'message': f'High disk usage: {(disk.used / disk.total) * 100:.1f}%'
                })
            
            return {
                'metrics': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': (disk.used / disk.total) * 100,
                    'memory_used_gb': memory.used / (1024**3),
                    'memory_total_gb': memory.total / (1024**3)
                },
                'alerts': alerts
            }
            
        except Exception as e:
            logger.error("Performance monitoring error", error=str(e))
            return {'error': str(e)}
    
    async def record_api_request(self, endpoint: str, method: str, status_code: int, 
                               response_time: float):
        """Record API request metrics"""
        self.request_count.labels(endpoint=endpoint, method=method, status=status_code).inc()
        self.response_time.labels(endpoint=endpoint, method=method).observe(response_time)
        
        if status_code >= 400:
            self.error_count.labels(endpoint=endpoint, error_type=f"{status_code}").inc()
    
    async def record_business_creation(self, business_id: str, success: bool, 
                                     revenue: float = 0, profit_margin: float = 0):
        """Record business creation metrics"""
        if success:
            self.businesses_created.inc()
            self.businesses_active.inc()
            if revenue > 0:
                self.revenue_generated.inc(revenue)
            if profit_margin > 0:
                self.profit_margin.set(profit_margin)
        else:
            self.businesses_failed.inc()
    
    async def record_agent_execution(self, agent_type: str, success: bool, 
                                   execution_time: float, error_type: str = None):
        """Record agent execution metrics"""
        status = 'success' if success else 'failed'
        self.agent_executions.labels(agent_type=agent_type, status=status).inc()
        self.agent_execution_time.labels(agent_type=agent_type).observe(execution_time)
        
        if not success and error_type:
            self.agent_errors.labels(agent_type=agent_type, error_type=error_type).inc()

class SecurityMonitor:
    """Enhanced security monitoring and threat detection"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
        # Security metrics
        self.security_events = Counter('security_events_total', 'Security events', ['event_type', 'severity'])
        self.failed_logins = Counter('failed_logins_total', 'Failed login attempts', ['ip_address'])
        self.suspicious_activities = Counter('suspicious_activities_total', 'Suspicious activities', ['activity_type'])
        self.blocked_ips = Gauge('blocked_ips_total', 'Total blocked IP addresses')
        self.active_threats = Gauge('active_threats', 'Currently active threats')
        
        self.threat_patterns = [
            r'sql injection',
            r'xss attack',
            r'csrf token',
            r'brute force',
            r'ddos attack',
            r'privilege escalation'
        ]
        
        self.rate_limits = {
            'login_attempts': 5,  # per hour
            'api_requests': 1000,  # per hour
            'business_creations': 10  # per hour
        }
    
    async def monitor_security_events(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and analyze security events"""
        try:
            event_type = event_data.get('type', 'unknown')
            severity = event_data.get('severity', 'low')
            ip_address = event_data.get('ip_address', 'unknown')
            user_id = event_data.get('user_id', 'unknown')
            
            # Record security event
            self.security_events.labels(event_type=event_type, severity=severity).inc()
            
            # Check for suspicious patterns
            threats_detected = await self._detect_threats(event_data)
            
            # Rate limiting checks
            rate_limit_violations = await self._check_rate_limits(event_data)
            
            # Generate alerts
            alerts = []
            
            if threats_detected:
                self.active_threats.inc()
                alerts.append({
                    'type': 'security',
                    'severity': 'critical',
                    'message': f'Threat detected: {", ".join(threats_detected)}'
                })
            
            if rate_limit_violations:
                alerts.append({
                    'type': 'security',
                    'severity': 'warning',
                    'message': f'Rate limit violation: {", ".join(rate_limit_violations)}'
                })
            
            # Block IP if necessary
            if severity == 'critical' or len(threats_detected) > 0:
                await self._block_ip(ip_address)
            
            return {
                'threats_detected': threats_detected,
                'rate_limit_violations': rate_limit_violations,
                'alerts': alerts,
                'ip_blocked': severity == 'critical' or len(threats_detected) > 0
            }
            
        except Exception as e:
            logger.error("Security monitoring error", error=str(e))
            return {'error': str(e)}
    
    async def _detect_threats(self, event_data: Dict[str, Any]) -> List[str]:
        """Detect security threats in event data"""
        threats = []
        
        # Check for suspicious patterns in request data
        request_data = event_data.get('request_data', '')
        if isinstance(request_data, str):
            for pattern in self.threat_patterns:
                if pattern.lower() in request_data.lower():
                    threats.append(pattern)
        
        # Check for unusual activity patterns
        user_id = event_data.get('user_id', '')
        if user_id:
            recent_events = await self._get_recent_events(user_id, minutes=5)
            if len(recent_events) > 50:  # Too many events in short time
                threats.append('unusual_activity_pattern')
        
        return threats
    
    async def _check_rate_limits(self, event_data: Dict[str, Any]) -> List[str]:
        """Check rate limiting violations"""
        violations = []
        
        event_type = event_data.get('type', '')
        user_id = event_data.get('user_id', '')
        ip_address = event_data.get('ip_address', '')
        
        if event_type == 'login_attempt':
            key = f"rate_limit:login:{ip_address}"
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, 3600)  # 1 hour
            
            if current > self.rate_limits['login_attempts']:
                violations.append('login_rate_limit')
        
        elif event_type == 'api_request':
            key = f"rate_limit:api:{user_id}"
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, 3600)  # 1 hour
            
            if current > self.rate_limits['api_requests']:
                violations.append('api_rate_limit')
        
        elif event_type == 'business_creation':
            key = f"rate_limit:business:{user_id}"
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, 3600)  # 1 hour
            
            if current > self.rate_limits['business_creations']:
                violations.append('business_creation_rate_limit')
        
        return violations
    
    async def _get_recent_events(self, user_id: str, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get recent events for a user"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            key = f"user_events:{user_id}"
            
            # This would typically query a database or cache
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error("Error getting recent events", error=str(e))
            return []
    
    async def _block_ip(self, ip_address: str) -> bool:
        """Block an IP address"""
        try:
            await self.redis.sadd("blocked_ips", ip_address)
            self.blocked_ips.inc()
            logger.warning("IP address blocked", ip_address=ip_address)
            return True
            
        except Exception as e:
            logger.error("Error blocking IP", error=str(e))
            return False

class QualityMonitor:
    """Enhanced quality monitoring for business creation and management"""
    
    def __init__(self):
        # Quality metrics
        self.quality_score = Gauge('quality_score', 'Quality score', ['business_id', 'metric_type'])
        self.quality_gates_passed = Counter('quality_gates_passed_total', 'Quality gates passed', ['gate_type'])
        self.quality_gates_failed = Counter('quality_gates_failed_total', 'Quality gates failed', ['gate_type'])
        self.business_viability = Gauge('business_viability_score', 'Business viability score', ['business_id'])
        self.customer_satisfaction = Gauge('customer_satisfaction_score', 'Customer satisfaction score', ['business_id'])
        
        self.quality_thresholds = {
            'viability_score': 0.7,
            'market_size': 1000000,
            'profit_margin': 0.2,
            'customer_satisfaction': 0.8
        }
    
    async def assess_business_quality(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess business quality across multiple dimensions"""
        try:
            business_id = business_data.get('business_id', 'unknown')
            
            # Market analysis quality
            market_score = await self._assess_market_quality(business_data.get('market_analysis', {}))
            self.quality_score.labels(business_id=business_id, metric_type='market').set(market_score)
            
            # Financial quality
            financial_score = await self._assess_financial_quality(business_data.get('financial_projections', {}))
            self.quality_score.labels(business_id=business_id, metric_type='financial').set(financial_score)
            
            # Operational quality
            operational_score = await self._assess_operational_quality(business_data.get('operational_plan', {}))
            self.quality_score.labels(business_id=business_id, metric_type='operational').set(operational_score)
            
            # Overall viability score
            viability_score = (market_score * 0.4 + financial_score * 0.4 + operational_score * 0.2)
            self.business_viability.labels(business_id=business_id).set(viability_score)
            
            # Quality gate decision
            passed = viability_score >= self.quality_thresholds['viability_score']
            
            if passed:
                self.quality_gates_passed.labels(gate_type='viability').inc()
                logger.info("Business passed viability quality gate", 
                          business_id=business_id, score=viability_score)
            else:
                self.quality_gates_failed.labels(gate_type='viability').inc()
                logger.warning("Business failed viability quality gate", 
                             business_id=business_id, score=viability_score)
            
            return {
                'passed': passed,
                'viability_score': viability_score,
                'market_score': market_score,
                'financial_score': financial_score,
                'operational_score': operational_score,
                'recommendations': await self._generate_quality_recommendations(business_data, viability_score)
            }
            
        except Exception as e:
            logger.error("Quality assessment error", error=str(e))
            return {'error': str(e)}
    
    async def _assess_market_quality(self, market_data: Dict[str, Any]) -> float:
        """Assess market analysis quality"""
        try:
            market_size = market_data.get('market_size', 0)
            growth_rate = market_data.get('growth_rate', 0)
            competition_level = market_data.get('competition_level', 0.5)
            
            # Market size score
            size_score = min(market_size / self.quality_thresholds['market_size'], 1.0)
            
            # Growth rate score
            growth_score = min(growth_rate / 0.1, 1.0)  # 10% growth = perfect
            
            # Competition score (moderate competition preferred)
            if competition_level <= 0.3:
                competition_score = 0.6  # Too little competition
            elif competition_level <= 0.7:
                competition_score = 1.0  # Good competition level
            else:
                competition_score = 0.4  # Too much competition
            
            return (size_score * 0.4 + growth_score * 0.4 + competition_score * 0.2)
            
        except Exception as e:
            logger.error("Market quality assessment error", error=str(e))
            return 0.0
    
    async def _assess_financial_quality(self, financial_data: Dict[str, Any]) -> float:
        """Assess financial projections quality"""
        try:
            profit_margin = financial_data.get('profit_margin', 0)
            revenue_projection = financial_data.get('revenue_projection', 0)
            break_even_months = financial_data.get('break_even_months', 24)
            
            # Profit margin score
            margin_score = min(profit_margin / self.quality_thresholds['profit_margin'], 1.0)
            
            # Revenue projection score
            revenue_score = min(revenue_projection / 1000000, 1.0)  # $1M = perfect
            
            # Break-even timeline score
            if break_even_months <= 6:
                timeline_score = 1.0
            elif break_even_months <= 12:
                timeline_score = 0.8
            elif break_even_months <= 18:
                timeline_score = 0.6
            else:
                timeline_score = 0.3
            
            return (margin_score * 0.4 + revenue_score * 0.4 + timeline_score * 0.2)
            
        except Exception as e:
            logger.error("Financial quality assessment error", error=str(e))
            return 0.0
    
    async def _assess_operational_quality(self, operational_data: Dict[str, Any]) -> float:
        """Assess operational plan quality"""
        try:
            team_size = operational_data.get('team_size', 1)
            technology_stack = operational_data.get('technology_stack', [])
            partnerships = operational_data.get('partnerships', [])
            
            # Team size score
            if team_size >= 5:
                team_score = 1.0
            elif team_size >= 3:
                team_score = 0.8
            elif team_size >= 2:
                team_score = 0.6
            else:
                team_score = 0.4
            
            # Technology stack score
            tech_score = min(len(technology_stack) / 5, 1.0)  # 5+ technologies = perfect
            
            # Partnerships score
            partnership_score = min(len(partnerships) / 3, 1.0)  # 3+ partnerships = perfect
            
            return (team_score * 0.4 + tech_score * 0.3 + partnership_score * 0.3)
            
        except Exception as e:
            logger.error("Operational quality assessment error", error=str(e))
            return 0.0
    
    async def _generate_quality_recommendations(self, business_data: Dict[str, Any], 
                                             viability_score: float) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        if viability_score < 0.5:
            recommendations.append("Consider pivoting to a different market or business model")
            recommendations.append("Increase market research and validation efforts")
            recommendations.append("Strengthen financial projections and funding strategy")
        
        if viability_score < 0.7:
            recommendations.append("Improve competitive positioning and differentiation")
            recommendations.append("Optimize pricing strategy for better profit margins")
            recommendations.append("Enhance operational efficiency and team structure")
        
        if viability_score < 0.8:
            recommendations.append("Strengthen partnerships and strategic alliances")
            recommendations.append("Improve technology stack and infrastructure")
            recommendations.append("Enhance customer acquisition and retention strategies")
        
        return recommendations

class EnhancedMonitoringSystem:
    """Main enhanced monitoring system that coordinates all monitoring components"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.performance_monitor = PerformanceMonitor()
        self.security_monitor = SecurityMonitor(redis_client)
        self.quality_monitor = QualityMonitor()
        
        self.alerts = []
        self.monitoring_active = True
        
        # System info
        self.system_info = Info('autopilot_system', 'AutoPilot Ventures system information')
        self.system_info.info({
            'version': '2.0.0',
            'deployment': 'production',
            'monitoring': 'enhanced'
        })
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        logger.info("Starting enhanced monitoring system")
        
        while self.monitoring_active:
            try:
                # Monitor system performance
                performance_status = await self.performance_monitor.monitor_system_performance()
                
                # Process any alerts
                if performance_status.get('alerts'):
                    for alert in performance_status['alerts']:
                        await self._process_alert(alert)
                
                # Wait before next monitoring cycle
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error("Monitoring cycle error", error=str(e))
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _process_alert(self, alert_data: Dict[str, Any]):
        """Process monitoring alerts"""
        try:
            alert = Alert(
                id=f"alert_{int(time.time())}",
                type=alert_data['type'],
                severity=alert_data['severity'],
                message=alert_data['message'],
                timestamp=datetime.now()
            )
            
            self.alerts.append(alert)
            
            logger.warning("Alert generated", 
                          alert_id=alert.id, type=alert.type, 
                          severity=alert.severity, message=alert.message)
            
            # Send alert to appropriate channels (email, Slack, etc.)
            await self._send_alert_notification(alert)
            
        except Exception as e:
            logger.error("Alert processing error", error=str(e))
    
    async def _send_alert_notification(self, alert: Alert):
        """Send alert notifications to appropriate channels"""
        try:
            # This would integrate with notification services
            # For now, just log the alert
            if alert.severity == 'critical':
                logger.critical("CRITICAL ALERT", 
                              alert_id=alert.id, message=alert.message)
            elif alert.severity == 'warning':
                logger.warning("WARNING ALERT", 
                             alert_id=alert.id, message=alert.message)
            
        except Exception as e:
            logger.error("Alert notification error", error=str(e))
    
    async def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary"""
        try:
            # Get performance metrics
            performance_status = await self.performance_monitor.monitor_system_performance()
            
            # Get active alerts
            active_alerts = [alert for alert in self.alerts if not alert.resolved]
            
            # Get system health score
            health_score = await self._calculate_health_score(performance_status)
            
            return {
                'health_score': health_score,
                'performance': performance_status,
                'active_alerts': len(active_alerts),
                'total_alerts': len(self.alerts),
                'system_status': 'healthy' if health_score > 0.8 else 'degraded' if health_score > 0.6 else 'critical'
            }
            
        except Exception as e:
            logger.error("Monitoring summary error", error=str(e))
            return {'error': str(e)}
    
    async def _calculate_health_score(self, performance_status: Dict[str, Any]) -> float:
        """Calculate overall system health score"""
        try:
            metrics = performance_status.get('metrics', {})
            
            # CPU health (lower is better)
            cpu_percent = metrics.get('cpu_percent', 0)
            cpu_health = max(0, 1 - (cpu_percent / 100))
            
            # Memory health (lower usage is better)
            memory_percent = metrics.get('memory_percent', 0)
            memory_health = max(0, 1 - (memory_percent / 100))
            
            # Disk health (lower usage is better)
            disk_percent = metrics.get('disk_percent', 0)
            disk_health = max(0, 1 - (disk_percent / 100))
            
            # Overall health score
            health_score = (cpu_health * 0.4 + memory_health * 0.4 + disk_health * 0.2)
            
            return health_score
            
        except Exception as e:
            logger.error("Health score calculation error", error=str(e))
            return 0.0
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        logger.info("Stopping enhanced monitoring system")
        self.monitoring_active = False

# Initialize the enhanced monitoring system
async def initialize_enhanced_monitoring(redis_url: str = "redis://localhost:6379") -> EnhancedMonitoringSystem:
    """Initialize the enhanced monitoring system"""
    try:
        redis_client = redis.from_url(redis_url)
        monitoring_system = EnhancedMonitoringSystem(redis_client)
        
        logger.info("Enhanced monitoring system initialized successfully")
        return monitoring_system
        
    except Exception as e:
        logger.error("Failed to initialize enhanced monitoring system", error=str(e))
        raise

if __name__ == "__main__":
    # Example usage
    async def main():
        monitoring_system = await initialize_enhanced_monitoring()
        
        # Start monitoring
        monitoring_task = asyncio.create_task(monitoring_system.start_monitoring())
        
        # Example business quality assessment
        business_data = {
            'business_id': 'business123',
            'market_analysis': {
                'market_size': 50000000,
                'growth_rate': 0.15,
                'competition_level': 0.6
            },
            'financial_projections': {
                'profit_margin': 0.25,
                'revenue_projection': 2000000,
                'break_even_months': 12
            },
            'operational_plan': {
                'team_size': 5,
                'technology_stack': ['AI', 'Cloud', 'Analytics'],
                'partnerships': ['Partner1', 'Partner2']
            }
        }
        
        quality_result = await monitoring_system.quality_monitor.assess_business_quality(business_data)
        print("Quality assessment result:", quality_result)
        
        # Get monitoring summary
        summary = await monitoring_system.get_monitoring_summary()
        print("Monitoring summary:", summary)
        
        # Stop monitoring after 60 seconds
        await asyncio.sleep(60)
        await monitoring_system.stop_monitoring()
        monitoring_task.cancel()
    
    asyncio.run(main()) 