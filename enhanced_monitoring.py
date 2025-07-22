#!/usr/bin/env python3
"""
Enhanced Monitoring System for AutoPilot Ventures Platform
Implements distributed tracing, APM, and comprehensive metrics collection
"""

import os
import json
import logging
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from functools import wraps
from contextlib import contextmanager
import uuid

# Monitoring imports
import prometheus_client as prometheus
from prometheus_client import Counter, Gauge, Histogram, Summary, Info
import structlog
from structlog import get_logger

# Distributed tracing
try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("OpenTelemetry not available. Distributed tracing disabled.")

# APM imports
try:
    from elasticapm import Client, capture_exception, capture_message
    APM_AVAILABLE = True
except ImportError:
    APM_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Elastic APM not available. APM monitoring disabled.")

from config import config
from utils import generate_id, log

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


class MetricsCollector:
    """Prometheus metrics collector."""
    
    def __init__(self):
        """Initialize metrics collector."""
        # Application metrics
        self.app_info = Info('autopilot_app', 'Application information')
        self.app_info.info({
            'version': '2.0.0',
            'environment': config.environment,
            'autonomy_level': config.autonomy_level
        })
        
        # Request metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )
        
        # Agent metrics
        self.agent_executions_total = Counter(
            'agent_executions_total',
            'Total agent executions',
            ['agent_type', 'status']
        )
        
        self.agent_execution_duration = Histogram(
            'agent_execution_duration_seconds',
            'Agent execution duration',
            ['agent_type']
        )
        
        # Business metrics
        self.startups_created_total = Counter(
            'startups_created_total',
            'Total startups created'
        )
        
        self.revenue_generated = Gauge(
            'revenue_generated_dollars',
            'Total revenue generated'
        )
        
        self.budget_used = Gauge(
            'budget_used_dollars',
            'Total budget used'
        )
        
        # System metrics
        self.active_users = Gauge(
            'active_users',
            'Number of active users'
        )
        
        self.active_startups = Gauge(
            'active_startups',
            'Number of active startups'
        )
        
        # Cache metrics
        self.cache_hits_total = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_type']
        )
        
        self.cache_misses_total = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_type']
        )
        
        # Database metrics
        self.db_queries_total = Counter(
            'db_queries_total',
            'Total database queries',
            ['operation', 'table']
        )
        
        self.db_query_duration = Histogram(
            'db_query_duration_seconds',
            'Database query duration',
            ['operation', 'table']
        )
        
        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total errors',
            ['error_type', 'component']
        )
        
        # Performance metrics
        self.memory_usage_bytes = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.cpu_usage_percent = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage'
        )
        
        logger.info("Metrics collector initialized")
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_agent_execution(self, agent_type: str, status: str, duration: float):
        """Record agent execution metrics."""
        self.agent_executions_total.labels(agent_type=agent_type, status=status).inc()
        self.agent_execution_duration.labels(agent_type=agent_type).observe(duration)
    
    def record_startup_created(self):
        """Record startup creation."""
        self.startups_created_total.inc()
    
    def record_revenue(self, amount: float):
        """Record revenue generation."""
        self.revenue_generated.inc(amount)
    
    def record_budget_used(self, amount: float):
        """Record budget usage."""
        self.budget_used.inc(amount)
    
    def set_active_users(self, count: int):
        """Set active users count."""
        self.active_users.set(count)
    
    def set_active_startups(self, count: int):
        """Set active startups count."""
        self.active_startups.set(count)
    
    def record_cache_hit(self, cache_type: str):
        """Record cache hit."""
        self.cache_hits_total.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str):
        """Record cache miss."""
        self.cache_misses_total.labels(cache_type=cache_type).inc()
    
    def record_db_query(self, operation: str, table: str, duration: float):
        """Record database query metrics."""
        self.db_queries_total.labels(operation=operation, table=table).inc()
        self.db_query_duration.labels(operation=operation, table=table).observe(duration)
    
    def record_error(self, error_type: str, component: str):
        """Record error metrics."""
        self.errors_total.labels(error_type=error_type, component=component).inc()
    
    def set_memory_usage(self, bytes_used: int):
        """Set memory usage."""
        self.memory_usage_bytes.set(bytes_used)
    
    def set_cpu_usage(self, percent: float):
        """Set CPU usage."""
        self.cpu_usage_percent.set(percent)


class DistributedTracer:
    """Distributed tracing with OpenTelemetry."""
    
    def __init__(self):
        """Initialize distributed tracer."""
        if not TRACING_AVAILABLE:
            self.tracer = None
            logger.warning("Distributed tracing not available")
            return
        
        try:
            # Initialize tracer provider
            trace.set_tracer_provider(TracerProvider())
            
            # Configure Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name=os.getenv('JAEGER_HOST', 'localhost'),
                agent_port=int(os.getenv('JAEGER_PORT', 6831))
            )
            
            # Add span processor
            trace.get_tracer_provider().add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )
            
            # Get tracer
            self.tracer = trace.get_tracer(__name__)
            
            logger.info("Distributed tracer initialized with Jaeger")
            
        except Exception as e:
            logger.error(f"Failed to initialize distributed tracer: {e}")
            self.tracer = None
    
    def start_span(self, name: str, attributes: Dict[str, Any] = None):
        """Start a new span."""
        if not self.tracer:
            return None
        
        try:
            span = self.tracer.start_span(name, attributes=attributes or {})
            return span
        except Exception as e:
            logger.error(f"Failed to start span: {e}")
            return None
    
    def add_event(self, span, name: str, attributes: Dict[str, Any] = None):
        """Add event to span."""
        if span:
            try:
                span.add_event(name, attributes=attributes or {})
            except Exception as e:
                logger.error(f"Failed to add event to span: {e}")
    
    def set_attribute(self, span, key: str, value: Any):
        """Set attribute on span."""
        if span:
            try:
                span.set_attribute(key, value)
            except Exception as e:
                logger.error(f"Failed to set span attribute: {e}")
    
    def end_span(self, span):
        """End span."""
        if span:
            try:
                span.end()
            except Exception as e:
                logger.error(f"Failed to end span: {e}")


class APMMonitor:
    """Application Performance Monitoring with Elastic APM."""
    
    def __init__(self):
        """Initialize APM monitor."""
        if not APM_AVAILABLE:
            self.client = None
            logger.warning("APM monitoring not available")
            return
        
        try:
            self.client = Client(
                service_name="autopilot-ventures",
                service_version="2.0.0",
                environment=config.environment,
                server_url=os.getenv('APM_SERVER_URL', 'http://localhost:8200'),
                secret_token=os.getenv('APM_SECRET_TOKEN', ''),
                transport_class='elasticapm.transport.http.Transport'
            )
            
            logger.info("APM monitor initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize APM monitor: {e}")
            self.client = None
    
    def capture_exception(self, exc_info=None, **kwargs):
        """Capture exception in APM."""
        if self.client:
            try:
                capture_exception(exc_info, **kwargs)
            except Exception as e:
                logger.error(f"Failed to capture exception in APM: {e}")
    
    def capture_message(self, message: str, level: str = 'info', **kwargs):
        """Capture message in APM."""
        if self.client:
            try:
                capture_message(message, level=level, **kwargs)
            except Exception as e:
                logger.error(f"Failed to capture message in APM: {e}")
    
    def start_transaction(self, name: str, transaction_type: str = 'request'):
        """Start APM transaction."""
        if self.client:
            try:
                return self.client.begin_transaction(transaction_type, name)
            except Exception as e:
                logger.error(f"Failed to start APM transaction: {e}")
        return None
    
    def end_transaction(self, result: str = 'success'):
        """End APM transaction."""
        if self.client:
            try:
                self.client.end_transaction(result)
            except Exception as e:
                logger.error(f"Failed to end APM transaction: {e}")


class PerformanceMonitor:
    """Performance monitoring and profiling."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        """Initialize performance monitor."""
        self.metrics = metrics_collector
        self.start_time = time.time()
    
    def monitor_function(self, func_name: str = None):
        """Decorator to monitor function performance."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                func_name_actual = func_name or func.__name__
                
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Record metrics
                    self.metrics.record_agent_execution(
                        agent_type=func_name_actual,
                        status='success',
                        duration=duration
                    )
                    
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    
                    # Record error metrics
                    self.metrics.record_agent_execution(
                        agent_type=func_name_actual,
                        status='error',
                        duration=duration
                    )
                    self.metrics.record_error(
                        error_type=type(e).__name__,
                        component=func_name_actual
                    )
                    
                    raise
            
            return wrapper
        return decorator
    
    @contextmanager
    def monitor_operation(self, operation_name: str, operation_type: str = 'general'):
        """Context manager to monitor operations."""
        start_time = time.time()
        
        try:
            yield
            duration = time.time() - start_time
            
            # Record success metrics
            if operation_type == 'db':
                self.metrics.record_db_query(operation_name, 'unknown', duration)
            else:
                self.metrics.record_agent_execution(operation_name, 'success', duration)
                
        except Exception as e:
            duration = time.time() - start_time
            
            # Record error metrics
            self.metrics.record_error(
                error_type=type(e).__name__,
                component=operation_name
            )
            
            if operation_type == 'db':
                self.metrics.record_db_query(operation_name, 'unknown', duration)
            else:
                self.metrics.record_agent_execution(operation_name, 'error', duration)
            
            raise
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds."""
        return time.time() - self.start_time
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        import psutil
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            
            # Update metrics
            self.metrics.set_memory_usage(memory_info.rss)
            self.metrics.set_cpu_usage(cpu_percent)
            
            return {
                'uptime_seconds': self.get_uptime(),
                'memory_usage_bytes': memory_info.rss,
                'memory_usage_mb': memory_info.rss / 1024 / 1024,
                'cpu_usage_percent': cpu_percent,
                'thread_count': process.num_threads(),
                'open_files': len(process.open_files()),
                'connections': len(process.connections())
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {}


class HealthChecker:
    """Health check system."""
    
    def __init__(self, metrics_collector: MetricsCollector, performance_monitor: PerformanceMonitor):
        """Initialize health checker."""
        self.metrics = metrics_collector
        self.performance = performance_monitor
        self.health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'environment': config.environment
        }
    
    def check_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            from database_postgresql import db_manager
            
            start_time = time.time()
            stats = db_manager.get_database_stats()
            duration = time.time() - start_time
            
            # Record database query metrics
            self.metrics.record_db_query('health_check', 'system', duration)
            
            return {
                'status': 'healthy',
                'response_time_ms': duration * 1000,
                'stats': stats
            }
            
        except Exception as e:
            self.metrics.record_error('database_connection', 'health_check')
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_cache_health(self) -> Dict[str, Any]:
        """Check cache health."""
        try:
            from redis_cache import cache_manager
            
            start_time = time.time()
            stats = cache_manager.get_stats()
            duration = time.time() - start_time
            
            return {
                'status': 'healthy' if stats.get('connected', False) else 'unhealthy',
                'response_time_ms': duration * 1000,
                'stats': stats
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_external_apis(self) -> Dict[str, Any]:
        """Check external API health."""
        try:
            import openai
            
            start_time = time.time()
            # Simple API call to check connectivity
            response = openai.Model.list(api_key=config.ai.openai_key)
            duration = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time_ms': duration * 1000,
                'models_available': len(response.data) if response.data else 0
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        try:
            # Check all components
            db_health = self.check_database_health()
            cache_health = self.check_cache_health()
            api_health = self.check_external_apis()
            performance_stats = self.performance.get_performance_stats()
            
            # Determine overall health
            all_healthy = all([
                db_health['status'] == 'healthy',
                cache_health['status'] == 'healthy',
                api_health['status'] == 'healthy'
            ])
            
            overall_status = 'healthy' if all_healthy else 'degraded'
            
            self.health_status.update({
                'status': overall_status,
                'timestamp': datetime.utcnow().isoformat(),
                'components': {
                    'database': db_health,
                    'cache': cache_health,
                    'external_apis': api_health
                },
                'performance': performance_stats,
                'uptime_seconds': self.performance.get_uptime()
            })
            
            return self.health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


class MonitoringMiddleware:
    """Monitoring middleware for FastAPI."""
    
    def __init__(self, metrics_collector: MetricsCollector, tracer: DistributedTracer, apm_monitor: APMMonitor):
        """Initialize monitoring middleware."""
        self.metrics = metrics_collector
        self.tracer = tracer
        self.apm_monitor = apm_monitor
    
    async def __call__(self, request, call_next):
        """Process request with monitoring."""
        start_time = time.time()
        
        # Start tracing
        span = None
        if self.tracer:
            span = self.tracer.start_span(
                f"{request.method} {request.url.path}",
                attributes={
                    'http.method': request.method,
                    'http.url': str(request.url),
                    'http.user_agent': request.headers.get('user-agent', ''),
                    'http.request_id': request.headers.get('x-request-id', str(uuid.uuid4()))
                }
            )
        
        # Start APM transaction
        apm_transaction = None
        if self.apm_monitor:
            apm_transaction = self.apm_monitor.start_transaction(
                f"{request.method} {request.url.path}",
                'request'
            )
        
        try:
            # Process request
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Record metrics
            self.metrics.record_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
            
            # Add tracing attributes
            if span:
                self.tracer.set_attribute(span, 'http.status_code', response.status_code)
                self.tracer.set_attribute(span, 'http.response_time_ms', duration * 1000)
            
            # End APM transaction
            if apm_transaction:
                self.apm_monitor.end_transaction('success')
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record error metrics
            self.metrics.record_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=500,
                duration=duration
            )
            self.metrics.record_error(
                error_type=type(e).__name__,
                component='http_request'
            )
            
            # Capture exception in APM
            if self.apm_monitor:
                self.apm_monitor.capture_exception()
                self.apm_monitor.end_transaction('error')
            
            # Add error to span
            if span:
                self.tracer.set_attribute(span, 'error', True)
                self.tracer.set_attribute(span, 'error.message', str(e))
            
            raise
        
        finally:
            # End span
            if span:
                self.tracer.end_span(span)


# Global monitoring instances
metrics_collector = MetricsCollector()
tracer = DistributedTracer()
apm_monitor = APMMonitor()
performance_monitor = PerformanceMonitor(metrics_collector)
health_checker = HealthChecker(metrics_collector, performance_monitor)
monitoring_middleware = MonitoringMiddleware(metrics_collector, tracer, apm_monitor)


# Monitoring decorators
def monitor_function(func_name: str = None):
    """Decorator to monitor function performance."""
    return performance_monitor.monitor_function(func_name)


def monitor_operation(operation_name: str, operation_type: str = 'general'):
    """Decorator to monitor operations."""
    return performance_monitor.monitor_operation(operation_name, operation_type)


# Health check endpoint
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return health_checker.get_comprehensive_health()


# Metrics endpoint
async def metrics() -> str:
    """Prometheus metrics endpoint."""
    return prometheus.generate_latest()


# Monitoring utilities
def record_error(error: Exception, component: str = 'unknown'):
    """Record error in monitoring systems."""
    # Record in metrics
    metrics_collector.record_error(type(error).__name__, component)
    
    # Capture in APM
    if apm_monitor:
        apm_monitor.capture_exception()
    
    # Log with structured logging
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        component=component,
        traceback=traceback.format_exc()
    )


def record_business_event(event_type: str, event_data: Dict[str, Any]):
    """Record business event in monitoring systems."""
    # Log business event
    logger.info(
        "Business event",
        event_type=event_type,
        **event_data
    )
    
    # Record in APM
    if apm_monitor:
        apm_monitor.capture_message(
            f"Business event: {event_type}",
            level='info',
            custom=event_data
        )


# Initialize monitoring
logger.info("Enhanced monitoring system initialized", 
           tracing_available=TRACING_AVAILABLE,
           apm_available=APM_AVAILABLE) 