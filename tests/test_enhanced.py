"""Enhanced tests for AutoPilot Ventures platform."""

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from config import config
from utils import (
    security_utils, budget_manager, generate_id, log,
    SecretsManager, AlertManager, RateLimiter
)
from database import db_manager, Startup, Agent, Task, Metrics
from agents import (
    NicheResearchAgent, MVPDesignAgent, MarketingStrategyAgent,
    ContentCreationAgent, AnalyticsAgent, OperationsMonetizationAgent,
    FundingInvestorAgent, LegalComplianceAgent, HRTeamBuildingAgent,
    CustomerSupportScalingAgent
)
from orchestrator import AgentOrchestrator, WorkflowStep, WorkflowResult
from main import AutoPilotVenturesApp


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response."""
    return Mock()
    mock_response.content = "Mock AI response for testing purposes."
    return mock_response


@pytest.fixture
def sample_startup_data():
    """Sample startup data for testing."""
    return {
        'name': 'Test Startup',
        'description': 'A test startup for automated testing',
        'niche': 'Technology',
        'language': 'en'
    }


@pytest.fixture
def sample_workflow_config():
    """Sample workflow configuration."""
    return {
        'niche_research': {
            'niche': 'AI-powered automation',
            'market_data': 'Growing market with high demand'
        },
        'mvp_design': {
            'niche': 'AI-powered automation',
            'target_audience': 'Small businesses',
            'requirements': 'User-friendly interface'
        },
        'marketing_strategy': {
            'product': 'AI Automation Platform',
            'target_audience': 'SMB owners',
            'budget': 1000.0
        },
        'funding_investor': {
            'startup_info': 'AI automation platform for SMBs',
            'funding_stage': 'seed',
            'target_amount': 50000.0
        },
        'legal_compliance': {
            'document_type': 'Terms of Service',
            'content': 'Standard terms and conditions',
            'jurisdiction': 'US'
        },
        'hr_team_building': {
            'company_info': 'AI automation startup',
            'hiring_needs': 'Developers and marketers',
            'team_size': 5
        },
        'customer_support_scaling': {
            'customer_queries': 'Technical support and billing questions',
            'current_scale': '50 customers',
            'language': 'en'
        }
    }


class TestEnhancedConfiguration:
    """Test enhanced configuration features."""

    def test_config_validation(self):
        """Test configuration validation."""
        assert config.ai.openai_key is not None
        assert config.security.fernet_key is not None
        assert len(config.multilingual.supported_languages) == 10
        assert config.monitoring.metrics_enabled is True

    def test_security_config(self):
        """Test security configuration."""
        assert config.security.content_safety_threshold > 0
        assert config.security.content_safety_threshold < 1
        assert config.security.secrets_manager_type in ['env', 'aws', 'azure']

    def test_monitoring_config(self):
        """Test monitoring configuration."""
        assert config.monitoring.prometheus_port > 0
        assert config.monitoring.budget_alert_threshold > 0
        assert config.monitoring.budget_alert_threshold < 1


class TestEnhancedSecurity:
    """Test enhanced security features."""

    def test_encryption_decryption(self):
        """Test encryption and decryption functionality."""
        test_data = "sensitive information"
        encrypted = security_utils.encrypt_data(test_data)
        decrypted = security_utils.decrypt_data(encrypted)
        assert decrypted == test_data

    def test_content_safety(self):
        """Test content safety checking."""
        safe_content = "This is a normal business message."
        safety_result = security_utils.check_content_safety(safe_content)
        assert 'toxicity' in safety_result
        assert safety_result['toxicity'] >= 0
        assert safety_result['toxicity'] <= 1

    def test_secrets_manager(self):
        """Test secrets manager functionality."""
        secrets_manager = SecretsManager()
        # Test environment variable fallback
        test_secret = secrets_manager.get_secret('TEST_SECRET')
        assert test_secret is None or isinstance(test_secret, str)


class TestEnhancedDatabase:
    """Test enhanced database features."""

    def test_enhanced_models(self):
        """Test enhanced database models."""
        # Test Startup model with new fields
        startup = Startup(
            id=generate_id("startup"),
            name="Test Startup",
            description="Test description",
            niche="Technology",
            funding_stage="seed",
            funding_raised=10000.0,
            valuation=100000.0,
            legal_status="compliant",
            team_size=5,
            customer_count=100,
            satisfaction_score=4.5
        )
        assert startup.name == "Test Startup"
        assert startup.funding_raised == 10000.0
        assert startup.team_size == 5

    def test_database_stats(self):
        """Test enhanced database statistics."""
        stats = db_manager.get_database_stats()
        assert 'startups' in stats
        assert 'agents' in stats
        assert 'funding_rounds' in stats
        assert 'legal_documents' in stats
        assert 'team_members' in stats
        assert 'support_tickets' in stats


class TestEnhancedAgents:
    """Test enhanced AI agents."""

    @pytest.mark.asyncio
    async def test_all_agents_initialization(self):
        """Test initialization of all 10 agents."""
        startup_id = generate_id("startup")
        
        agents = {
            'niche_research': NicheResearchAgent(startup_id),
            'mvp_design': MVPDesignAgent(startup_id),
            'marketing_strategy': MarketingStrategyAgent(startup_id),
            'content_creation': ContentCreationAgent(startup_id),
            'analytics': AnalyticsAgent(startup_id),
            'operations_monetization': OperationsMonetizationAgent(startup_id),
            'funding_investor': FundingInvestorAgent(startup_id),
            'legal_compliance': LegalComplianceAgent(startup_id),
            'hr_team_building': HRTeamBuildingAgent(startup_id),
            'customer_support_scaling': CustomerSupportScalingAgent(startup_id)
        }
        
        assert len(agents) == 10
        for agent_type, agent in agents.items():
            assert agent.agent_type == agent_type
            assert agent.startup_id == startup_id
            assert hasattr(agent, 'execute')

    @pytest.mark.asyncio
    @patch('agents.ChatOpenAI')
    async def test_funding_investor_agent(self, mock_llm):
        """Test funding and investor relations agent."""
        startup_id = generate_id("startup")
        agent = FundingInvestorAgent(startup_id)
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Mock funding strategy response"
        mock_llm.return_value.invoke.return_value = mock_response
        
        result = await agent.execute(
            startup_info="AI automation platform",
            funding_stage="seed",
            target_amount=50000.0
        )
        
        assert hasattr(result, 'success')
        assert hasattr(result, 'data')
        assert hasattr(result, 'cost')

    @pytest.mark.asyncio
    @patch('agents.ChatOpenAI')
    async def test_legal_compliance_agent(self, mock_llm):
        """Test legal and compliance agent."""
        startup_id = generate_id("startup")
        agent = LegalComplianceAgent(startup_id)
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Mock legal analysis response"
        mock_llm.return_value.invoke.return_value = mock_response
        
        result = await agent.execute(
            document_type="Terms of Service",
            content="Standard terms and conditions",
            jurisdiction="US"
        )
        
        assert hasattr(result, 'success')
        assert hasattr(result, 'data')
        assert hasattr(result, 'cost')

    @pytest.mark.asyncio
    @patch('agents.ChatOpenAI')
    async def test_hr_team_building_agent(self, mock_llm):
        """Test HR and team building agent."""
        startup_id = generate_id("startup")
        agent = HRTeamBuildingAgent(startup_id)
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Mock HR strategy response"
        mock_llm.return_value.invoke.return_value = mock_response
        
        result = await agent.execute(
            company_info="AI automation startup",
            hiring_needs="Developers and marketers",
            team_size=5
        )
        
        assert hasattr(result, 'success')
        assert hasattr(result, 'data')
        assert hasattr(result, 'cost')

    @pytest.mark.asyncio
    @patch('agents.ChatOpenAI')
    async def test_customer_support_scaling_agent(self, mock_llm):
        """Test customer support and scaling agent."""
        startup_id = generate_id("startup")
        agent = CustomerSupportScalingAgent(startup_id)
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Mock support strategy response"
        mock_llm.return_value.invoke.return_value = mock_response
        
        result = await agent.execute(
            customer_queries="Technical support questions",
            current_scale="50 customers",
            language="en"
        )
        
        assert hasattr(result, 'success')
        assert hasattr(result, 'data')
        assert hasattr(result, 'cost')


class TestEnhancedOrchestrator:
    """Test enhanced orchestrator."""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        startup_id = generate_id("startup")
        orchestrator = AgentOrchestrator(startup_id)
        
        assert orchestrator.startup_id == startup_id
        assert len(orchestrator.agents) == 10
        assert len(orchestrator.workflow_steps) == 10

    def test_workflow_steps(self):
        """Test workflow step configuration."""
        startup_id = generate_id("startup")
        orchestrator = AgentOrchestrator(startup_id)
        
        # Check that all 10 agents are included
        agent_types = [step.agent_type for step in orchestrator.workflow_steps]
        expected_types = [
            'niche_research', 'mvp_design', 'marketing_strategy',
            'content_creation', 'analytics', 'operations_monetization',
            'funding_investor', 'legal_compliance', 'hr_team_building',
            'customer_support_scaling'
        ]
        
        assert set(agent_types) == set(expected_types)

    @pytest.mark.asyncio
    async def test_workflow_execution(self, sample_workflow_config):
        """Test workflow execution."""
        startup_id = generate_id("startup")
        orchestrator = AgentOrchestrator(startup_id)
        
        # Mock budget manager to allow spending
        with patch.object(budget_manager, 'can_spend', return_value=True):
            with patch.object(budget_manager, 'spend', return_value=True):
                # Mock agent execution
                with patch.object(orchestrator, '_execute_step') as mock_execute:
                    mock_execute.return_value = {
                        'success': True,
                        'data': {'test': 'data'},
                        'cost': 0.1
                    }
                    
                    result = await orchestrator.execute_workflow(sample_workflow_config)
                    
                    assert isinstance(result, WorkflowResult)
                    assert result.startup_id == startup_id
                    assert len(result.steps_completed) > 0

    def test_agent_performance(self):
        """Test agent performance tracking."""
        startup_id = generate_id("startup")
        orchestrator = AgentOrchestrator(startup_id)
        
        performance = orchestrator.get_agent_performance()
        assert len(performance) == 10
        
        for agent_type, perf in performance.items():
            assert 'execution_count' in perf
            assert 'success_rate' in perf
            assert 'status' in perf


class TestEnhancedMainApp:
    """Test enhanced main application."""

    @pytest.mark.asyncio
    async def test_app_initialization(self):
        """Test application initialization."""
        app = AutoPilotVenturesApp()
        assert len(app.agents) == 10
        assert app.startup_id is None
        assert app.orchestrator is None

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test comprehensive health check."""
        app = AutoPilotVenturesApp()
        health_status = await app.health_check()
        
        assert 'status' in health_status
        assert 'timestamp' in health_status
        assert 'version' in health_status
        assert 'checks' in health_status
        
        checks = health_status['checks']
        assert 'database' in checks
        assert 'budget' in checks
        assert 'security' in checks
        assert 'agents' in checks
        assert 'configuration' in checks

    @pytest.mark.asyncio
    async def test_startup_creation(self, sample_startup_data):
        """Test startup creation with enhanced features."""
        app = AutoPilotVenturesApp()
        
        result = await app.create_startup(
            name=sample_startup_data['name'],
            description=sample_startup_data['description'],
            niche=sample_startup_data['niche'],
            language=sample_startup_data['language']
        )
        
        assert result['success'] is True
        assert 'startup_id' in result
        assert result['language'] == sample_startup_data['language']

    @pytest.mark.asyncio
    async def test_multilingual_demo(self):
        """Test multilingual demonstration."""
        app = AutoPilotVenturesApp()
        
        # Test with different languages
        for language in ['en', 'es', 'zh', 'fr', 'de']:
            result = await app.multilingual_demo(language)
            assert result['success'] is True
            assert result['language'] == language
            assert 'cultural_context' in result

    def test_platform_status(self):
        """Test platform status reporting."""
        app = AutoPilotVenturesApp()
        status = app.get_platform_status()
        
        assert status['platform_version'] == '2.0.0'
        assert status['total_agents'] == 10
        assert len(status['agent_types']) == 10
        assert 'supported_languages' in status
        assert 'budget_status' in status
        assert 'monitoring' in status
        assert 'security' in status


class TestEnhancedMonitoring:
    """Test enhanced monitoring features."""

    def test_prometheus_metrics(self):
        """Test Prometheus metrics configuration."""
        from utils import (
            AGENT_EXECUTION_COUNTER, AGENT_EXECUTION_DURATION,
            BUDGET_USAGE_GAUGE, API_CALLS_COUNTER
        )
        
        assert AGENT_EXECUTION_COUNTER is not None
        assert AGENT_EXECUTION_DURATION is not None
        assert BUDGET_USAGE_GAUGE is not None
        assert API_CALLS_COUNTER is not None

    def test_alert_manager(self):
        """Test alert manager functionality."""
        alert_manager = AlertManager()
        
        # Test email alert (should fail without SMTP config)
        email_result = alert_manager.send_email_alert("Test", "Test message")
        assert email_result is False
        
        # Test Slack alert (should fail without webhook)
        slack_result = alert_manager.send_slack_alert("Test message")
        assert slack_result is False

    def test_rate_limiter(self):
        """Test rate limiting functionality."""
        rate_limiter = RateLimiter()
        
        # Test rate limit check
        result = rate_limiter.check_rate_limit("test_identifier")
        assert result is True


class TestEnhancedBudgetManagement:
    """Test enhanced budget management."""

    def test_budget_operations(self):
        """Test budget operations."""
        # Reset budget for testing
        budget_manager.remaining_budget = 100.0
        budget_manager.initial_budget = 100.0
        
        # Test spending
        assert budget_manager.can_spend(50.0) is True
        assert budget_manager.spend(50.0) is True
        assert budget_manager.get_remaining_budget() == 50.0
        
        # Test insufficient budget
        assert budget_manager.can_spend(100.0) is False
        assert budget_manager.spend(100.0) is False

    def test_daily_spending_limit(self):
        """Test daily spending limits."""
        # Reset daily spent
        budget_manager.daily_spent = 0.0
        
        # Test daily limit
        assert budget_manager.can_spend(25.0) is True
        assert budget_manager.spend(25.0) is True
        
        # Should still be under daily limit
        assert budget_manager.get_daily_spent() == 25.0


class TestEnhancedMultilingualSupport:
    """Test enhanced multilingual support."""

    def test_supported_languages(self):
        """Test supported languages configuration."""
        supported_languages = config.multilingual.supported_languages
        expected_languages = ['en', 'es', 'zh', 'fr', 'de', 'ar', 'pt', 'hi', 'ru', 'ja']
        
        assert len(supported_languages) == 10
        assert set(supported_languages) == set(expected_languages)

    def test_language_validation(self):
        """Test language validation."""
        app = AutoPilotVenturesApp()
        
        # Test valid language
        result = app.create_startup("Test", "Description", "Tech", "es")
        assert result['language'] == 'es'
        
        # Test invalid language (should default to 'en')
        result = app.create_startup("Test", "Description", "Tech", "invalid")
        assert result['language'] == 'en'


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 