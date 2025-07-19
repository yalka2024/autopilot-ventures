"""Basic tests for AutoPilot Ventures platform."""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from config import config, AIConfig, SecurityConfig, DatabaseConfig, BudgetConfig
from utils import (
    generate_id, sanitize_filename, validate_email, validate_url,
    sanitize_html, SecurityUtils, BudgetManager, TimeUtils, MetricsUtils
)
from database import (
    db_manager, Startup, Agent, Task, Metrics, DatabaseManager
)
from agents import (
    BaseAgent, NicheResearchAgent, MVPDesignAgent, MarketingStrategyAgent,
    ContentCreationAgent, AnalyticsAgent, OperationsMonetizationAgent,
    AgentResult
)
from main import AutoPilotVenturesApp


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Create temporary database manager
    temp_db_manager = DatabaseManager(f"sqlite:///{db_path}")
    
    yield temp_db_manager
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def mock_openai_key():
    """Mock OpenAI API key for testing."""
    with patch.dict(os.environ, {'OPENAI_SECRET_KEY': 'test-key-123'}):
        yield 'test-key-123'


@pytest.fixture
def mock_fernet_key():
    """Mock Fernet key for testing."""
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    with patch.dict(os.environ, {'FERNET_KEY': key.decode()}):
        yield key.decode()


@pytest.fixture
def sample_startup_data():
    """Sample startup data for testing."""
    return {
        'name': 'Test Startup',
        'description': 'A test startup for testing',
        'niche': 'technology',
        'metadata': {'test': True}
    }


class TestConfig:
    """Test configuration management."""
    
    def test_ai_config_creation(self):
        """Test AI configuration creation."""
        ai_config = AIConfig()
        assert ai_config.model_name == 'gpt-4'
        assert ai_config.max_tokens == 4000
        assert ai_config.temperature == 0.7
    
    def test_security_config_creation(self):
        """Test security configuration creation."""
        security_config = SecurityConfig()
        assert security_config.content_safety_threshold == 0.7
        assert security_config.max_file_size == 10 * 1024 * 1024
        assert 'autopilotventures.com' in security_config.allowed_domains
    
    def test_database_config_creation(self):
        """Test database configuration creation."""
        db_config = DatabaseConfig()
        assert db_config.backup_interval == 24
        assert db_config.max_startups == 100
    
    def test_budget_config_creation(self):
        """Test budget configuration creation."""
        budget_config = BudgetConfig()
        assert budget_config.initial_budget == 500.0
        assert budget_config.cost_per_request == 0.01
        assert budget_config.max_daily_spend == 50.0
    
    def test_config_fernet_key_validation(self, mock_fernet_key):
        """Test Fernet key validation in config."""
        config_obj = config
        assert config_obj.security.fernet_key == mock_fernet_key


class TestUtils:
    """Test utility functions."""
    
    def test_generate_id(self):
        """Test ID generation."""
        id1 = generate_id("test")
        id2 = generate_id("test")
        
        assert id1.startswith("test_")
        assert id2.startswith("test_")
        assert id1 != id2
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        unsafe_name = "file<>:\"/\\|?*.txt"
        safe_name = sanitize_filename(unsafe_name)
        
        assert "<" not in safe_name
        assert ">" not in safe_name
        assert ":" not in safe_name
        assert '"' not in safe_name
        assert "/" not in safe_name
        assert "\\" not in safe_name
        assert "|" not in safe_name
        assert "?" not in safe_name
        assert "*" not in safe_name
    
    def test_validate_email(self):
        """Test email validation."""
        assert validate_email("test@example.com") is True
        assert validate_email("invalid-email") is False
        assert validate_email("test@.com") is False
        assert validate_email("") is False
    
    def test_validate_url(self):
        """Test URL validation."""
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com") is True
        assert validate_url("invalid-url") is False
        assert validate_url("") is False
    
    def test_sanitize_html(self):
        """Test HTML sanitization."""
        unsafe_html = "<script>alert('xss')</script><p>Safe content</p>"
        safe_html = sanitize_html(unsafe_html)
        
        assert "<script>" not in safe_html
        assert "<p>Safe content</p>" in safe_html
    
    def test_security_utils_encryption(self, mock_fernet_key):
        """Test security utils encryption."""
        security = SecurityUtils(mock_fernet_key)
        test_data = "test data"
        
        encrypted = security.encrypt_data(test_data)
        decrypted = security.decrypt_data(encrypted)
        
        assert decrypted == test_data
        assert encrypted != test_data
    
    def test_security_utils_content_safety(self, mock_fernet_key):
        """Test content safety checking."""
        security = SecurityUtils(mock_fernet_key)
        
        # Test safe content
        safe_result = security.check_content_safety("This is safe content")
        assert 'toxicity' in safe_result
        
        # Test potentially unsafe content
        unsafe_result = security.check_content_safety("This contains hate speech")
        assert 'toxicity' in unsafe_result
    
    def test_budget_manager(self):
        """Test budget manager functionality."""
        budget = BudgetManager(100.0)
        
        assert budget.get_remaining_budget() == 100.0
        assert budget.can_spend(50.0) is True
        assert budget.can_spend(150.0) is False
        
        assert budget.spend(30.0) is True
        assert budget.get_remaining_budget() == 70.0
        
        budget.add_funds(20.0)
        assert budget.get_remaining_budget() == 90.0
    
    def test_time_utils(self):
        """Test time utilities."""
        timestamp = TimeUtils.get_timestamp()
        assert isinstance(timestamp, str)
        
        duration = TimeUtils.format_duration(3661)
        assert "1h 1m" in duration
        
        assert TimeUtils.is_business_day(datetime.now()) in [True, False]
    
    def test_metrics_utils(self):
        """Test metrics utilities."""
        roi = MetricsUtils.calculate_roi(100.0, 150.0)
        assert roi == 0.5
        
        growth_rate = MetricsUtils.calculate_growth_rate(100.0, 121.0, 2)
        assert abs(growth_rate - 0.1) < 0.01
        
        engagement = MetricsUtils.calculate_engagement_rate(50, 1000)
        assert engagement == 5.0


class TestDatabase:
    """Test database operations."""
    
    def test_create_startup(self, temp_db):
        """Test startup creation."""
        startup = temp_db.create_startup(
            name="Test Startup",
            description="Test description",
            niche="technology"
        )
        
        assert startup.name == "Test Startup"
        assert startup.description == "Test description"
        assert startup.niche == "technology"
        assert startup.id.startswith("startup_")
    
    def test_get_startup(self, temp_db):
        """Test startup retrieval."""
        startup = temp_db.create_startup(
            name="Test Startup",
            description="Test description",
            niche="technology"
        )
        
        retrieved = temp_db.get_startup(startup.id)
        assert retrieved is not None
        assert retrieved.name == startup.name
    
    def test_update_startup(self, temp_db):
        """Test startup update."""
        startup = temp_db.create_startup(
            name="Test Startup",
            description="Test description",
            niche="technology"
        )
        
        updated = temp_db.update_startup(startup.id, {
            'name': 'Updated Startup',
            'status': 'inactive'
        })
        
        assert updated.name == 'Updated Startup'
        assert updated.status == 'inactive'
    
    def test_delete_startup(self, temp_db):
        """Test startup deletion."""
        startup = temp_db.create_startup(
            name="Test Startup",
            description="Test description",
            niche="technology"
        )
        
        success = temp_db.delete_startup(startup.id)
        assert success is True
        
        retrieved = temp_db.get_startup(startup.id)
        assert retrieved is None
    
    def test_create_agent(self, temp_db):
        """Test agent creation."""
        startup = temp_db.create_startup(
            name="Test Startup",
            description="Test description",
            niche="technology"
        )
        
        agent = temp_db.create_agent(
            startup_id=startup.id,
            agent_type="niche_research"
        )
        
        assert agent.startup_id == startup.id
        assert agent.agent_type == "niche_research"
        assert agent.id.startswith("agent_")
    
    def test_create_task(self, temp_db):
        """Test task creation."""
        startup = temp_db.create_startup(
            name="Test Startup",
            description="Test description",
            niche="technology"
        )
        
        task = temp_db.create_task(
            startup_id=startup.id,
            task_type="research",
            description="Test task",
            priority=1
        )
        
        assert task.startup_id == startup.id
        assert task.task_type == "research"
        assert task.description == "Test task"
        assert task.priority == 1
    
    def test_create_metric(self, temp_db):
        """Test metric creation."""
        startup = temp_db.create_startup(
            name="Test Startup",
            description="Test description",
            niche="technology"
        )
        
        metric = temp_db.create_metric(
            startup_id=startup.id,
            metric_type="revenue",
            value=1000.0
        )
        
        assert metric.startup_id == startup.id
        assert metric.metric_type == "revenue"
        assert metric.value == 1000.0
    
    def test_database_stats(self, temp_db):
        """Test database statistics."""
        stats = temp_db.get_database_stats()
        
        assert 'startups' in stats
        assert 'agents' in stats
        assert 'tasks' in stats
        assert 'metrics' in stats
        assert isinstance(stats['startups'], int)


class TestAgents:
    """Test AI agents."""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        mock_response = Mock()
        mock_response.content = "Test response content"
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        
        return mock_llm
    
    def test_base_agent_initialization(self, mock_fernet_key):
        """Test base agent initialization."""
        with patch('agents.ChatOpenAI') as mock_chat:
            mock_chat.return_value = Mock()
            
            agent = BaseAgent('test_agent', 'test_startup_id')
            
            assert agent.agent_type == 'test_agent'
            assert agent.startup_id == 'test_startup_id'
            assert agent.agent_id.startswith('agent_test_agent')
    
    @pytest.mark.asyncio
    async def test_niche_research_agent(self, mock_llm, mock_fernet_key):
        """Test niche research agent."""
        with patch('agents.ChatOpenAI', return_value=mock_llm):
            with patch('agents.db_manager') as mock_db:
                mock_db.create_agent.return_value = Mock()
                mock_db.get_agents_by_startup.return_value = [Mock()]
                mock_db.update_agent.return_value = Mock()
                
                agent = NicheResearchAgent('test_startup_id')
                result = await agent.execute(niche="technology")
                
                assert isinstance(result, AgentResult)
                assert result.success is True
                assert 'analysis' in result.data
    
    @pytest.mark.asyncio
    async def test_mvp_design_agent(self, mock_llm, mock_fernet_key):
        """Test MVP design agent."""
        with patch('agents.ChatOpenAI', return_value=mock_llm):
            with patch('agents.db_manager') as mock_db:
                mock_db.create_agent.return_value = Mock()
                mock_db.get_agents_by_startup.return_value = [Mock()]
                mock_db.update_agent.return_value = Mock()
                
                agent = MVPDesignAgent('test_startup_id')
                result = await agent.execute(
                    niche="technology",
                    target_audience="developers"
                )
                
                assert isinstance(result, AgentResult)
                assert result.success is True
                assert 'mvp_design' in result.data
    
    @pytest.mark.asyncio
    async def test_marketing_strategy_agent(self, mock_llm, mock_fernet_key):
        """Test marketing strategy agent."""
        with patch('agents.ChatOpenAI', return_value=mock_llm):
            with patch('agents.db_manager') as mock_db:
                mock_db.create_agent.return_value = Mock()
                mock_db.get_agents_by_startup.return_value = [Mock()]
                mock_db.update_agent.return_value = Mock()
                
                agent = MarketingStrategyAgent('test_startup_id')
                result = await agent.execute(
                    product="SaaS platform",
                    target_audience="businesses",
                    budget=1000.0
                )
                
                assert isinstance(result, AgentResult)
                assert result.success is True
                assert 'marketing_strategy' in result.data
    
    @pytest.mark.asyncio
    async def test_content_creation_agent(self, mock_llm, mock_fernet_key):
        """Test content creation agent."""
        with patch('agents.ChatOpenAI', return_value=mock_llm):
            with patch('agents.db_manager') as mock_db:
                mock_db.create_agent.return_value = Mock()
                mock_db.get_agents_by_startup.return_value = [Mock()]
                mock_db.update_agent.return_value = Mock()
                
                agent = ContentCreationAgent('test_startup_id')
                result = await agent.execute(
                    topic="AI in business",
                    audience="executives"
                )
                
                assert isinstance(result, AgentResult)
                assert result.success is True
                assert 'content' in result.data
    
    @pytest.mark.asyncio
    async def test_analytics_agent(self, mock_llm, mock_fernet_key):
        """Test analytics agent."""
        with patch('agents.ChatOpenAI', return_value=mock_llm):
            with patch('agents.db_manager') as mock_db:
                mock_db.create_agent.return_value = Mock()
                mock_db.get_agents_by_startup.return_value = [Mock()]
                mock_db.update_agent.return_value = Mock()
                
                agent = AnalyticsAgent('test_startup_id')
                result = await agent.execute(
                    data="User engagement metrics",
                    metrics="Conversion rates"
                )
                
                assert isinstance(result, AgentResult)
                assert result.success is True
                assert 'analysis' in result.data
    
    @pytest.mark.asyncio
    async def test_operations_monetization_agent(self, mock_llm, mock_fernet_key):
        """Test operations monetization agent."""
        with patch('agents.ChatOpenAI', return_value=mock_llm):
            with patch('agents.db_manager') as mock_db:
                mock_db.create_agent.return_value = Mock()
                mock_db.get_agents_by_startup.return_value = [Mock()]
                mock_db.update_agent.return_value = Mock()
                
                agent = OperationsMonetizationAgent('test_startup_id')
                result = await agent.execute(
                    current_operations="Subscription model",
                    revenue_data="Monthly recurring revenue"
                )
                
                assert isinstance(result, AgentResult)
                assert result.success is True
                assert 'optimization_plan' in result.data


class TestMainApp:
    """Test main application."""
    
    @pytest.fixture
    def mock_app(self, mock_fernet_key):
        """Mock application for testing."""
        with patch('main.config') as mock_config:
            mock_config.ai.openai_key = 'test-key'
            mock_config.security.fernet_key = mock_fernet_key
            
            with patch('main.security_utils') as mock_security:
                mock_security.encrypt_data.return_value = 'encrypted'
                mock_security.decrypt_data.return_value = 'test'
                
                app = AutoPilotVenturesApp()
                return app
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_app):
        """Test health check functionality."""
        with patch('main.db_manager') as mock_db:
            mock_db.get_database_stats.return_value = {
                'startups': 5,
                'agents': 10,
                'tasks': 15,
                'metrics': 20
            }
            mock_db.create_startup.return_value = Mock(id='test_id')
            mock_db.create_agent.return_value = Mock()
            mock_db.delete_startup.return_value = True
            
            with patch('main.budget_manager') as mock_budget:
                mock_budget.get_remaining_budget.return_value = 100.0
                mock_budget.get_daily_spent.return_value = 10.0
                mock_budget.can_spend.return_value = True
                
                with patch('main.security_utils') as mock_security:
                    mock_security.encrypt_data.return_value = 'encrypted'
                    mock_security.decrypt_data.return_value = 'test'
                    mock_security.check_content_safety.return_value = {
                        'toxicity': 0.1
                    }
                    
                    results = await mock_app.health_check()

                    assert 'status' in results
                    assert 'checks' in results
                    assert 'timestamp' in results
    
    @pytest.mark.asyncio
    async def test_create_startup(self, mock_app):
        """Test startup creation."""
        with patch('main.db_manager') as mock_db:
            mock_startup = Mock()
            mock_startup.id = 'test_startup_id'
            mock_db.create_startup.return_value = mock_startup
            
            with patch.object(mock_app, '_initialize_agents'):
                result = await mock_app.create_startup(
                    name="Test Startup",
                    description="Test description",
                    niche="technology"
                )
                
                assert result['success'] is True
                assert result['startup_id'] == 'test_startup_id'
    
    @pytest.mark.asyncio
    async def test_multilingual_demo(self, mock_app):
        """Test multilingual demo."""
        with patch('main.db_manager') as mock_db:
            mock_startup = Mock()
            mock_startup.id = 'test_startup_id'
            mock_db.create_startup.return_value = mock_startup
            
            with patch.object(mock_app, '_initialize_agents'):
                with patch.object(mock_app, 'run_niche_research') as mock_research:
                    mock_research.return_value = {'success': True}
                    
                    result = await mock_app.demo_multilingual_startup('hi')
                    
                    assert result['success'] is True
                    assert 'research_result' in result
    
    def test_get_metrics(self, mock_app):
        """Test metrics retrieval."""
        with patch('main.db_manager') as mock_db:
            mock_db.get_database_stats.return_value = {
                'startups': 5,
                'agents': 10,
                'tasks': 15,
                'metrics': 20
            }
            
            with patch('main.budget_manager') as mock_budget:
                mock_budget.get_remaining_budget.return_value = 100.0
                mock_budget.get_daily_spent.return_value = 10.0
                mock_budget.can_spend.return_value = True
                
                metrics = mock_app.get_metrics()
                
                assert 'database' in metrics
                assert 'budget' in metrics
                assert 'timestamp' in metrics
                assert 'supported_languages' in metrics 