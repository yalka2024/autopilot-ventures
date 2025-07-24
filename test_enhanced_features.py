"""
Comprehensive Test Suite for Enhanced AutoPilot Ventures Features
Tests health monitoring, BigQuery analytics, and self-healing CI/CD
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import json

# Import our enhanced modules
from health_monitoring import HealthMonitor, HealthStatus, HealthCheck
from bigquery_analytics import BigQueryAnalytics, RequestLog, BusinessMetric, SystemMetric
from self_healing_cicd import SelfHealingCICD, DeploymentStatus, FailureType, DeploymentEvent

class TestHealthMonitoring:
    """Test health monitoring system"""
    
    @pytest.fixture
    def health_monitor(self):
        return HealthMonitor()
    
    @pytest.mark.asyncio
    async def test_startup_probe_success(self, health_monitor):
        """Test successful startup probe"""
        with patch('health_monitoring.psutil') as mock_psutil:
            mock_psutil.virtual_memory.return_value.percent = 50
            mock_psutil.disk_usage.return_value.percent = 60
            
            with patch('health_monitoring.requests.get') as mock_requests:
                mock_requests.return_value.status_code = 200
                
                result = await health_monitor.startup_probe()
                assert result == True
                assert len(health_monitor.startup_probes) > 0
    
    @pytest.mark.asyncio
    async def test_startup_probe_failure(self, health_monitor):
        """Test failed startup probe"""
        with patch('health_monitoring.psutil') as mock_psutil:
            mock_psutil.virtual_memory.return_value.percent = 95  # High memory usage
            mock_psutil.disk_usage.return_value.percent = 60
            
            result = await health_monitor.startup_probe()
            assert result == False
    
    @pytest.mark.asyncio
    async def test_health_check_comprehensive(self, health_monitor):
        """Test comprehensive health check"""
        with patch('health_monitoring.requests.get') as mock_requests:
            mock_requests.return_value.status_code = 200
            mock_requests.return_value.elapsed.total_seconds.return_value = 0.1
            
            result = await health_monitor.health_check()
            
            assert 'status' in result
            assert 'timestamp' in result
            assert 'checks' in result
            assert 'system_metrics' in result
    
    @pytest.mark.asyncio
    async def test_health_check_api_endpoints(self, health_monitor):
        """Test API endpoints health check"""
        with patch('health_monitoring.requests.get') as mock_requests:
            mock_requests.return_value.status_code = 200
            mock_requests.return_value.elapsed.total_seconds.return_value = 0.1
            
            result = await health_monitor._check_api_endpoints()
            
            assert 'status' in result
            assert 'message' in result
            assert 'details' in result
    
    def test_system_metrics(self, health_monitor):
        """Test system metrics collection"""
        with patch('health_monitoring.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 25.0
            mock_psutil.virtual_memory.return_value.percent = 50.0
            mock_psutil.disk_usage.return_value.percent = 60.0
            
            metrics = health_monitor._get_system_metrics()
            
            assert 'cpu_percent' in metrics
            assert 'memory_percent' in metrics
            assert 'disk_percent' in metrics
            assert 'uptime_seconds' in metrics

class TestBigQueryAnalytics:
    """Test BigQuery analytics system"""
    
    @pytest.fixture
    def bigquery_analytics(self):
        with patch('bigquery_analytics.bigquery'):
            return BigQueryAnalytics(project_id="test-project")
    
    def test_request_log_creation(self, bigquery_analytics):
        """Test request log creation"""
        request_log = RequestLog(
            timestamp=datetime.now().isoformat(),
            request_id="test-123",
            method="GET",
            path="/health",
            status_code=200,
            response_time_ms=150.5,
            user_agent="test-agent",
            ip_address="127.0.0.1",
            language="en"
        )
        
        assert request_log.request_id == "test-123"
        assert request_log.method == "GET"
        assert request_log.status_code == 200
        assert request_log.response_time_ms == 150.5
    
    def test_business_metric_creation(self, bigquery_analytics):
        """Test business metric creation"""
        business_metric = BusinessMetric(
            timestamp=datetime.now().isoformat(),
            business_id="business-123",
            metric_name="revenue",
            metric_value=1000.0,
            metric_unit="USD",
            category="financial",
            tags={"region": "US", "product": "premium"}
        )
        
        assert business_metric.business_id == "business-123"
        assert business_metric.metric_name == "revenue"
        assert business_metric.metric_value == 1000.0
        assert business_metric.category == "financial"
    
    def test_system_metric_creation(self, bigquery_analytics):
        """Test system metric creation"""
        system_metric = SystemMetric(
            timestamp=datetime.now().isoformat(),
            metric_name="cpu_usage",
            metric_value=75.5,
            metric_unit="percentage",
            component="web_server",
            tags={"instance": "primary"}
        )
        
        assert system_metric.metric_name == "cpu_usage"
        assert system_metric.metric_value == 75.5
        assert system_metric.component == "web_server"
    
    def test_log_request(self, bigquery_analytics):
        """Test request logging"""
        request_log = RequestLog(
            timestamp=datetime.now().isoformat(),
            request_id="test-123",
            method="GET",
            path="/health",
            status_code=200,
            response_time_ms=150.5,
            user_agent="test-agent",
            ip_address="127.0.0.1",
            language="en"
        )
        
        bigquery_analytics.log_request(request_log)
        assert len(bigquery_analytics.request_logs_queue) == 1
    
    def test_log_business_metric(self, bigquery_analytics):
        """Test business metric logging"""
        business_metric = BusinessMetric(
            timestamp=datetime.now().isoformat(),
            business_id="business-123",
            metric_name="revenue",
            metric_value=1000.0,
            metric_unit="USD",
            category="financial"
        )
        
        bigquery_analytics.log_business_metric(business_metric)
        assert len(bigquery_analytics.business_metrics_queue) == 1
    
    def test_log_system_metric(self, bigquery_analytics):
        """Test system metric logging"""
        system_metric = SystemMetric(
            timestamp=datetime.now().isoformat(),
            metric_name="cpu_usage",
            metric_value=75.5,
            metric_unit="percentage",
            component="web_server"
        )
        
        bigquery_analytics.log_system_metric(system_metric)
        assert len(bigquery_analytics.system_metrics_queue) == 1
    
    def test_get_analytics_queries(self, bigquery_analytics):
        """Test analytics query generation"""
        queries = bigquery_analytics.get_analytics_query("request_analysis")
        assert "SELECT" in queries
        assert "FROM" in queries
        assert "request_logs" in queries

class TestSelfHealingCICD:
    """Test self-healing CI/CD system"""
    
    @pytest.fixture
    def cicd(self):
        return SelfHealingCICD(project_id="test-project")
    
    def test_deployment_event_creation(self, cicd):
        """Test deployment event creation"""
        event = DeploymentEvent(
            event_id="deploy-123",
            timestamp=datetime.now(),
            status=DeploymentStatus.SUCCESS,
            duration_seconds=120.5,
            metadata={"image_tag": "v1.0.0", "environment": "production"}
        )
        
        assert event.event_id == "deploy-123"
        assert event.status == DeploymentStatus.SUCCESS
        assert event.duration_seconds == 120.5
    
    @pytest.mark.asyncio
    async def test_deploy_success(self, cicd):
        """Test successful deployment"""
        with patch('self_healing_cicd.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            with patch.object(cicd, '_pre_deployment_check', return_value=True):
                with patch.object(cicd, '_post_deployment_check', return_value=True):
                    with patch.object(cicd, '_validate_performance', return_value=True):
                        
                        result = await cicd.deploy("v1.0.0", "production")
                        assert result == True
    
    @pytest.mark.asyncio
    async def test_deploy_failure(self, cicd):
        """Test failed deployment"""
        with patch('self_healing_cicd.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Deployment failed"
            
            result = await cicd.deploy("v1.0.0", "production")
            assert result == False
    
    @pytest.mark.asyncio
    async def test_health_check_performance(self, cicd):
        """Test health check performance"""
        with patch('self_healing_cicd.requests.get') as mock_requests:
            mock_requests.return_value.status_code = 200
            mock_requests.return_value.elapsed.total_seconds.return_value = 0.05
            
            result = await cicd._perform_health_check()
            
            assert result.status == "healthy"
            assert result.response_time_ms < 100
    
    @pytest.mark.asyncio
    async def test_trigger_recovery(self, cicd):
        """Test recovery triggering"""
        cicd.recovery_attempts = 0
        
        with patch.object(cicd, '_restart_service', return_value=True):
            await cicd._trigger_recovery()
            assert cicd.recovery_attempts == 1
    
    @pytest.mark.asyncio
    async def test_trigger_rollback(self, cicd):
        """Test rollback triggering"""
        # Add a successful deployment to history
        successful_event = DeploymentEvent(
            event_id="deploy-success",
            timestamp=datetime.now(),
            status=DeploymentStatus.SUCCESS,
            metadata={"image_tag": "v0.9.0"}
        )
        cicd.deployment_history.append(successful_event)
        
        with patch.object(cicd, 'deploy', return_value=True):
            await cicd._trigger_rollback()
    
    def test_get_deployment_status(self, cicd):
        """Test deployment status retrieval"""
        status = cicd.get_deployment_status()
        
        assert 'current_deployment' in status
        assert 'deployment_status' in status
        assert 'recovery_attempts' in status
        assert 'total_deployments' in status
    
    def test_get_deployment_history(self, cicd):
        """Test deployment history retrieval"""
        # Add some test deployments
        for i in range(5):
            event = DeploymentEvent(
                event_id=f"deploy-{i}",
                timestamp=datetime.now(),
                status=DeploymentStatus.SUCCESS if i % 2 == 0 else DeploymentStatus.FAILED
            )
            cicd.deployment_history.append(event)
        
        history = cicd.get_deployment_history(limit=3)
        assert len(history) == 3

class TestIntegration:
    """Integration tests for all enhanced features"""
    
    @pytest.mark.asyncio
    async def test_full_deployment_workflow(self):
        """Test complete deployment workflow with all features"""
        # Initialize all systems
        health_monitor = HealthMonitor()
        bigquery_analytics = BigQueryAnalytics(project_id="test-project")
        cicd = SelfHealingCICD(project_id="test-project")
        
        # Mock all external dependencies
        with patch('health_monitoring.psutil') as mock_psutil:
            mock_psutil.virtual_memory.return_value.percent = 50
            mock_psutil.disk_usage.return_value.percent = 60
            
            with patch('health_monitoring.requests.get') as mock_requests:
                mock_requests.return_value.status_code = 200
                mock_requests.return_value.elapsed.total_seconds.return_value = 0.1
                
                # Test startup probe
                startup_result = await health_monitor.startup_probe()
                assert startup_result == True
                
                # Test health check
                health_result = await health_monitor.health_check()
                assert 'status' in health_result
                
                # Test deployment
                with patch('self_healing_cicd.subprocess.run') as mock_run:
                    mock_run.return_value.returncode = 0
                    
                    deploy_result = await cicd.deploy("v1.0.0", "production")
                    assert deploy_result == True
                
                # Test analytics logging
                request_log = RequestLog(
                    timestamp=datetime.now().isoformat(),
                    request_id="integration-test",
                    method="GET",
                    path="/health",
                    status_code=200,
                    response_time_ms=100.0,
                    user_agent="integration-test",
                    ip_address="127.0.0.1",
                    language="en"
                )
                
                bigquery_analytics.log_request(request_log)
                assert len(bigquery_analytics.request_logs_queue) == 1
    
    @pytest.mark.asyncio
    async def test_failure_recovery_workflow(self):
        """Test failure detection and recovery workflow"""
        cicd = SelfHealingCICD(project_id="test-project")
        
        # Simulate deployment failure
        with patch('self_healing_cicd.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Deployment failed"
            
            # Deploy should fail
            result = await cicd.deploy("v1.0.0", "production")
            assert result == False
            
            # Check that failure was recorded
            assert len(cicd.deployment_history) > 0
            assert cicd.deployment_history[-1].status == DeploymentStatus.FAILED
    
    def test_metrics_collection_workflow(self):
        """Test comprehensive metrics collection workflow"""
        bigquery_analytics = BigQueryAnalytics(project_id="test-project")
        
        # Log various types of metrics
        request_log = RequestLog(
            timestamp=datetime.now().isoformat(),
            request_id="metrics-test",
            method="POST",
            path="/business/create",
            status_code=201,
            response_time_ms=250.0,
            user_agent="metrics-test",
            ip_address="127.0.0.1",
            language="en"
        )
        
        business_metric = BusinessMetric(
            timestamp=datetime.now().isoformat(),
            business_id="business-123",
            metric_name="revenue",
            metric_value=5000.0,
            metric_unit="USD",
            category="financial"
        )
        
        system_metric = SystemMetric(
            timestamp=datetime.now().isoformat(),
            metric_name="memory_usage",
            metric_value=65.5,
            metric_unit="percentage",
            component="web_server"
        )
        
        # Log all metrics
        bigquery_analytics.log_request(request_log)
        bigquery_analytics.log_business_metric(business_metric)
        bigquery_analytics.log_system_metric(system_metric)
        
        # Verify all metrics are queued
        assert len(bigquery_analytics.request_logs_queue) == 1
        assert len(bigquery_analytics.business_metrics_queue) == 1
        assert len(bigquery_analytics.system_metrics_queue) == 1

if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "--tb=short"]) 