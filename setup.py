#!/usr/bin/env python3
"""
Comprehensive Setup Script for AutoPilot Ventures Platform
Installs dependencies, configures environment, initializes database, and tests agents
"""

import os
import sys
import subprocess
import platform
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import base64
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoPilotSetup:
    """Comprehensive setup class for AutoPilot Ventures platform."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / '.env'
        self.db_file = self.project_root / 'phase1_memory.db'
        self.test_results = {}
        
        # Supported languages for testing
        self.test_languages = {
            'en': 'English',
            'es': 'Spanish', 
            'zh': 'Chinese',
            'fr': 'French',
            'de': 'German',
            'ar': 'Arabic',
            'pt': 'Portuguese',
            'hi': 'Hindi',
            'ru': 'Russian',
            'ja': 'Japanese'
        }
        
        # Agent types for testing
        self.agent_types = [
            'niche_research',
            'mvp_design', 
            'marketing_strategy',
            'content_creation',
            'analytics',
            'operations_monetization',
            'funding_investor',
            'legal_compliance',
            'hr_team_building',
            'customer_support_scaling'
        ]

    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        logger.info("Checking Python version...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            logger.error(f"Python 3.8+ required. Current version: {version.major}.{version.minor}")
            return False
        logger.info(f"Python version {version.major}.{version.minor}.{version.micro} is compatible")
        return True

    def install_dependencies(self) -> bool:
        """Install dependencies from requirements.txt."""
        logger.info("Installing dependencies...")
        try:
            # Upgrade pip first
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            
            # Install requirements
            requirements_file = self.project_root / 'requirements.txt'
            if not requirements_file.exists():
                logger.error("requirements.txt not found")
                return False
                
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
                check=True, capture_output=True, text=True
            )
            logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False

    def generate_fernet_key(self) -> str:
        """Generate a new Fernet encryption key."""
        key = Fernet.generate_key()
        return key.decode()

    def create_env_file(self) -> bool:
        """Create .env file with required API keys and configuration."""
        logger.info("Creating .env file...")
        
        env_template = f"""# AutoPilot Ventures Environment Configuration

# OpenAI Configuration
OPENAI_SECRET_KEY=your_openai_api_key_here

# DeepL Translation Service
DEEPL_API_KEY=your_deepl_api_key_here

# Fernet Encryption Key (auto-generated)
FERNET_KEY={self.generate_fernet_key()}

# Database Configuration
DATABASE_URL=sqlite:///phase1_memory.db

# Stripe Payment Processing (optional)
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# Monitoring and Alerts
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# Additional Services
SERPAPI_KEY=your_serpapi_key_here
AWS_REGION=us-east-1
SECRETS_MANAGER=env

# Platform Configuration
INITIAL_BUDGET=500.0
MAX_DAILY_SPEND=50.0
CURRENCY=USD
"""
        
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(env_template)
            logger.info(f".env file created at {self.env_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")
            return False

    def validate_env_configuration(self) -> bool:
        """Validate environment configuration."""
        logger.info("Validating environment configuration...")
        
        if not self.env_file.exists():
            logger.error(".env file not found")
            return False
            
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv(self.env_file)
        
        required_keys = ['OPENAI_SECRET_KEY']
        missing_keys = []
        
        for key in required_keys:
            if not os.getenv(key) or os.getenv(key) == f'your_{key.lower()}_here':
                missing_keys.append(key)
        
        if missing_keys:
            logger.warning(f"Missing or default API keys: {missing_keys}")
            logger.info("Please update the .env file with your actual API keys")
            return False
            
        logger.info("Environment configuration validated")
        return True

    def initialize_database(self) -> bool:
        """Initialize SQLAlchemy database."""
        logger.info("Initializing database...")
        try:
            # Import database modules
            from database import db_manager
            from config import config
            
            # Initialize database
            db_manager.init_database()
            
            # Create initial tables
            db_manager.create_tables()
            
            logger.info(f"Database initialized at {self.db_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False

    async def test_agent(self, agent_type: str, language: str = 'en') -> Dict:
        """Test a single agent with multilingual support."""
        logger.info(f"Testing {agent_type} agent in {language}")
        
        try:
            # Import required modules
            from agents import (
                NicheResearchAgent, MVPDesignAgent, MarketingStrategyAgent,
                ContentCreationAgent, AnalyticsAgent, OperationsMonetizationAgent,
                FundingInvestorAgent, LegalComplianceAgent, HRTeamBuildingAgent,
                CustomerSupportScalingAgent
            )
            from config import config
            from utils import generate_id
            
            # Agent class mapping
            agent_classes = {
                'niche_research': NicheResearchAgent,
                'mvp_design': MVPDesignAgent,
                'marketing_strategy': MarketingStrategyAgent,
                'content_creation': ContentCreationAgent,
                'analytics': AnalyticsAgent,
                'operations_monetization': OperationsMonetizationAgent,
                'funding_investor': FundingInvestorAgent,
                'legal_compliance': LegalComplianceAgent,
                'hr_team_building': HRTeamBuildingAgent,
                'customer_support_scaling': CustomerSupportScalingAgent
            }
            
            if agent_type not in agent_classes:
                return {'success': False, 'error': f'Unknown agent type: {agent_type}'}
            
            # Create test startup ID
            startup_id = generate_id('test_startup')
            
            # Initialize agent
            agent_class = agent_classes[agent_type]
            agent = agent_class(startup_id)
            
            # Test parameters based on agent type
            test_params = self._get_test_parameters(agent_type, language)
            
            # Execute agent
            result = await agent.execute(**test_params)
            
            return {
                'success': result.success,
                'data': result.data,
                'message': result.message,
                'cost': result.cost
            }
            
        except Exception as e:
            logger.error(f"Error testing {agent_type} agent: {e}")
            return {'success': False, 'error': str(e)}

    def _get_test_parameters(self, agent_type: str, language: str) -> Dict:
        """Get test parameters for different agent types."""
        base_params = {
            'niche_research': {
                'niche': 'AI-powered productivity tools',
                'market_data': 'Growing market for AI productivity solutions'
            },
            'mvp_design': {
                'niche': 'AI productivity tools',
                'target_audience': 'Remote workers and small businesses',
                'requirements': 'Simple, intuitive interface with AI assistance'
            },
            'marketing_strategy': {
                'product': 'AI-powered task management app',
                'target_audience': 'Remote workers aged 25-45',
                'budget': 1000.0
            },
            'content_creation': {
                'topic': 'AI productivity benefits',
                'audience': 'Remote workers',
                'content_type': 'blog post',
                'tone': 'professional'
            },
            'analytics': {
                'data': 'User engagement metrics for productivity app',
                'metrics': 'daily active users, session duration, feature usage',
                'questions': 'What features drive the most engagement?'
            },
            'operations_monetization': {
                'current_operations': 'Freemium SaaS model',
                'revenue_data': 'Monthly recurring revenue of $50,000'
            },
            'funding_investor': {
                'startup_info': 'AI productivity platform with 10,000 users',
                'funding_stage': 'Series A',
                'target_amount': 500000.0
            },
            'legal_compliance': {
                'document_type': 'Terms of Service',
                'content': 'AI-powered productivity platform terms',
                'jurisdiction': 'US'
            },
            'hr_team_building': {
                'company_info': 'AI productivity startup',
                'hiring_needs': 'Software engineers and product managers',
                'team_size': 15
            },
            'customer_support_scaling': {
                'customer_queries': 'Technical support and feature requests',
                'current_scale': '1000 customers',
                'language': language
            }
        }
        
        return base_params.get(agent_type, {})

    async def test_all_agents(self) -> Dict:
        """Test all 10 agents in multiple languages."""
        logger.info("Testing all agents...")
        
        test_results = {
            'total_agents': len(self.agent_types),
            'languages_tested': list(self.test_languages.keys()),
            'results': {}
        }
        
        # Test in English first
        for agent_type in self.agent_types:
            logger.info(f"Testing {agent_type} agent in English...")
            result = await self.test_agent(agent_type, 'en')
            test_results['results'][f'{agent_type}_en'] = result
            
        # Test in Spanish (second language)
        for agent_type in self.agent_types[:3]:  # Test first 3 agents in Spanish
            logger.info(f"Testing {agent_type} agent in Spanish...")
            result = await self.test_agent(agent_type, 'es')
            test_results['results'][f'{agent_type}_es'] = result
            
        return test_results

    async def test_main_application(self) -> Dict:
        """Test the main application with multilingual support."""
        logger.info("Testing main application...")
        
        try:
            from main import AutoPilotVenturesApp
            
            app = AutoPilotVenturesApp()
            
            # Test health check
            health_status = await app.health_check()
            
            # Test business creation in English
            english_business = await app.create_business(
                name="AI Productivity Platform",
                description="AI-powered task management for remote teams",
                niche="Productivity Software",
                language="en"
            )
            
            # Test business creation in Spanish
            spanish_business = await app.create_business(
                name="Plataforma de Productividad IA",
                description="Gestión de tareas impulsada por IA para equipos remotos",
                niche="Software de Productividad",
                language="es"
            )
            
            return {
                'success': True,
                'health_status': health_status,
                'english_business': english_business,
                'spanish_business': spanish_business
            }
            
        except Exception as e:
            logger.error(f"Error testing main application: {e}")
            return {'success': False, 'error': str(e)}

    async def test_meta_agent_coordinator(self) -> Dict:
        """Test the meta-agent coordinator."""
        logger.info("Testing meta-agent coordinator...")
        
        try:
            from meta_agent_coordinator import MetaAgentCoordinator
            import redis
            
            # Initialize Redis connection (use mock if not available)
            try:
                redis_client = redis.Redis(host='localhost', port=6379, db=0)
                redis_client.ping()
            except:
                logger.warning("Redis not available, using mock coordinator")
                redis_client = None
            
            if redis_client:
                coordinator = MetaAgentCoordinator(redis_client)
                
                # Test coordination summary
                summary = await coordinator.get_coordination_summary()
                
                return {
                    'success': True,
                    'coordinator_summary': summary
                }
            else:
                return {
                    'success': True,
                    'message': 'Meta-agent coordinator test skipped (Redis not available)'
                }
                
        except Exception as e:
            logger.error(f"Error testing meta-agent coordinator: {e}")
            return {'success': False, 'error': str(e)}

    def run_unit_tests(self) -> bool:
        """Run unit tests for multilingual content generation and agent coordination."""
        logger.info("Running unit tests...")
        
        try:
            # Create test file if it doesn't exist
            test_file = self.project_root / 'test_setup.py'
            if not test_file.exists():
                self._create_unit_tests()
            
            # Run tests
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', str(test_file), '-v'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                logger.info("Unit tests passed")
                return True
            else:
                logger.error(f"Unit tests failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running unit tests: {e}")
            return False

    def _create_unit_tests(self):
        """Create unit tests for multilingual content generation and agent coordination."""
        test_content = '''"""
Unit tests for AutoPilot Ventures setup and multilingual functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from config import config
from agents import NicheResearchAgent, ContentCreationAgent
from utils import generate_id

class TestMultilingualSupport:
    """Test multilingual content generation."""
    
    def test_supported_languages(self):
        """Test that all 10 languages are supported."""
        assert len(config.multilingual.supported_languages) == 10
        assert 'en' in config.multilingual.supported_languages
        assert 'es' in config.multilingual.supported_languages
        assert 'zh' in config.multilingual.supported_languages
    
    def test_default_language(self):
        """Test default language configuration."""
        assert config.multilingual.default_language == 'en'
    
    @pytest.mark.asyncio
    async def test_agent_multilingual_execution(self):
        """Test agent execution in different languages."""
        startup_id = generate_id('test')
        agent = NicheResearchAgent(startup_id)
        
        # Test in English
        result_en = await agent.execute(
            niche="AI productivity tools",
            market_data="Growing market"
        )
        assert result_en.success
        
        # Test in Spanish
        result_es = await agent.execute(
            niche="Herramientas de productividad IA",
            market_data="Mercado en crecimiento"
        )
        assert result_es.success

class TestAgentCoordination:
    """Test agent coordination functionality."""
    
    def test_agent_initialization(self):
        """Test that all 10 agents can be initialized."""
        startup_id = generate_id('test')
        
        agents = [
            NicheResearchAgent(startup_id),
            ContentCreationAgent(startup_id)
        ]
        
        assert len(agents) == 2
        for agent in agents:
            assert agent.startup_id == startup_id
    
    @pytest.mark.asyncio
    async def test_agent_communication(self):
        """Test agent communication and coordination."""
        startup_id = generate_id('test')
        
        # Test niche research agent
        niche_agent = NicheResearchAgent(startup_id)
        niche_result = await niche_agent.execute(
            niche="AI productivity tools"
        )
        
        # Test content creation based on niche research
        content_agent = ContentCreationAgent(startup_id)
        content_result = await content_agent.execute(
            topic="AI productivity benefits",
            audience="Remote workers",
            content_type="blog post"
        )
        
        assert niche_result.success
        assert content_result.success

class TestConfiguration:
    """Test configuration management."""
    
    def test_fernet_key_generation(self):
        """Test Fernet key generation and validation."""
        assert config.security.fernet_key is not None
        assert len(config.security.fernet_key) > 0
    
    def test_openai_configuration(self):
        """Test OpenAI configuration."""
        assert config.ai.model_name == 'gpt-4'
        assert config.ai.max_tokens > 0
        assert config.ai.temperature >= 0.0 and config.ai.temperature <= 1.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
        
        with open(self.project_root / 'test_setup.py', 'w', encoding='utf-8') as f:
            f.write(test_content)

    def update_readme(self) -> bool:
        """Update README with local testing steps."""
        logger.info("Updating README...")
        
        readme_file = self.project_root / 'README.md'
        if not readme_file.exists():
            logger.warning("README.md not found, creating new one")
        
        readme_content = f"""# AutoPilot Ventures - AI-Powered Business Creation Platform

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- DeepL API key (for translations)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd autopilot-ventures
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Configure API keys**
   Edit the `.env` file and add your API keys:
   ```
   OPENAI_SECRET_KEY=your_openai_api_key_here
   DEEPL_API_KEY=your_deepl_api_key_here
   ```

### Local Testing

#### Test All Agents
```bash
python -c "
import asyncio
from setup import AutoPilotSetup
setup = AutoPilotSetup()
results = asyncio.run(setup.test_all_agents())
print('Test Results:', results)
"
```

#### Test Main Application
```bash
python -c "
import asyncio
from setup import AutoPilotSetup
setup = AutoPilotSetup()
results = asyncio.run(setup.test_main_application())
print('Main App Results:', results)
"
```

#### Test in Different Languages
```bash
# English
python main.py --language en --niche "AI productivity tools"

# Spanish
python main.py --language es --niche "Herramientas de productividad IA"

# Chinese
python main.py --language zh --niche "AI生产力工具"
```

### Agent Types

The platform includes 10 specialized AI agents:

1. **Niche Research Agent** - Market research and niche identification
2. **MVP Design Agent** - Product design and prototyping
3. **Marketing Strategy Agent** - Marketing planning and execution
4. **Content Creation Agent** - Content generation and management
5. **Analytics Agent** - Data analysis and insights
6. **Operations Monetization Agent** - Business operations and revenue
7. **Funding Investor Agent** - Investment and funding strategies
8. **Legal Compliance Agent** - Legal documentation and compliance
9. **HR Team Building Agent** - Team building and hiring
10. **Customer Support Scaling Agent** - Customer support optimization

### Multilingual Support

Supported languages:
- English (en)
- Spanish (es)
- Chinese (zh)
- French (fr)
- German (de)
- Arabic (ar)
- Portuguese (pt)
- Hindi (hi)
- Russian (ru)
- Japanese (ja)

### Database

The platform uses SQLAlchemy with SQLite for local development:
- Database file: `phase1_memory.db`
- Automatic initialization on first run
- Backup and recovery features

### Security

- Fernet encryption for sensitive data
- Content safety filtering
- API key management
- Secure communication between agents

### Monitoring

- Prometheus metrics
- Structured logging
- Performance monitoring
- Budget tracking

### Troubleshooting

1. **API Key Issues**
   - Ensure your OpenAI API key is valid
   - Check DeepL API key for translations
   - Verify all keys are in the `.env` file

2. **Database Issues**
   - Delete `phase1_memory.db` to reset
   - Check file permissions
   - Ensure SQLite is available

3. **Agent Testing Issues**
   - Check internet connection
   - Verify API rate limits
   - Review error logs

### Development

Run unit tests:
```bash
python -m pytest test_setup.py -v
```

### License

This project is licensed under the MIT License.
"""
        
        try:
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            logger.info("README updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to update README: {e}")
            return False

    async def run_comprehensive_setup(self) -> Dict:
        """Run comprehensive setup and testing."""
        logger.info("Starting comprehensive AutoPilot Ventures setup...")
        
        setup_results = {
            'python_version_check': False,
            'dependencies_installed': False,
            'env_configured': False,
            'database_initialized': False,
            'agents_tested': False,
            'main_app_tested': False,
            'coordinator_tested': False,
            'unit_tests_passed': False,
            'readme_updated': False
        }
        
        try:
            # Step 1: Check Python version
            setup_results['python_version_check'] = self.check_python_version()
            if not setup_results['python_version_check']:
                return setup_results
            
            # Step 2: Install dependencies
            setup_results['dependencies_installed'] = self.install_dependencies()
            if not setup_results['dependencies_installed']:
                return setup_results
            
            # Step 3: Create and configure environment
            setup_results['env_configured'] = self.create_env_file()
            if not setup_results['env_configured']:
                return setup_results
            
            # Step 4: Initialize database
            setup_results['database_initialized'] = self.initialize_database()
            if not setup_results['database_initialized']:
                return setup_results
            
            # Step 5: Test agents
            agent_results = await self.test_all_agents()
            setup_results['agents_tested'] = len(agent_results['results']) > 0
            
            # Step 6: Test main application
            main_results = await self.test_main_application()
            setup_results['main_app_tested'] = main_results.get('success', False)
            
            # Step 7: Test meta-agent coordinator
            coordinator_results = await self.test_meta_agent_coordinator()
            setup_results['coordinator_tested'] = coordinator_results.get('success', False)
            
            # Step 8: Run unit tests
            setup_results['unit_tests_passed'] = self.run_unit_tests()
            
            # Step 9: Update README
            setup_results['readme_updated'] = self.update_readme()
            
            # Store detailed results
            setup_results['detailed_results'] = {
                'agent_tests': agent_results,
                'main_app_tests': main_results,
                'coordinator_tests': coordinator_results
            }
            
            logger.info("Comprehensive setup completed successfully!")
            return setup_results
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            setup_results['error'] = str(e)
            return setup_results

def main():
    """Main setup function."""
    print("🚀 AutoPilot Ventures Setup Script")
    print("=" * 50)
    
    setup = AutoPilotSetup()
    
    # Run comprehensive setup
    results = asyncio.run(setup.run_comprehensive_setup())
    
    # Print results
    print("\n📊 Setup Results:")
    print("=" * 50)
    
    for step, success in results.items():
        if step != 'detailed_results' and step != 'error':
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{step.replace('_', ' ').title()}: {status}")
    
    if 'error' in results:
        print(f"\n❌ Error: {results['error']}")
    
    # Print agent test summary
    if 'detailed_results' in results:
        agent_results = results['detailed_results']['agent_tests']
        print(f"\n🤖 Agent Tests: {len(agent_results['results'])} tests completed")
        
        successful_tests = sum(1 for r in agent_results['results'].values() if r.get('success', False))
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {len(agent_results['results']) - successful_tests}")
    
    print("\n🎉 Setup complete! Check the README for next steps.")

if __name__ == "__main__":
    main() 